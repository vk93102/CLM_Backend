import json
import os
import re
import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


def _templates_dir() -> str:
    return os.path.join(settings.BASE_DIR, "templates")


def _meta_path_for_template(template_path: str) -> str:
    return f"{template_path}.meta.json"


def _json_safe(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _read_template_meta(template_path: str) -> dict:
    meta_path = _meta_path_for_template(template_path)
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_template_meta(template_path: str, meta: dict) -> None:
    meta_path = _meta_path_for_template(template_path)
    with open(meta_path, "w", encoding="utf-8", newline="") as f:
        json.dump(_json_safe(meta or {}), f, ensure_ascii=False, indent=2)


def _infer_template_type(filename: str) -> str:
    name = filename.lower()
    if "nda" in name:
        return "NDA"
    if "sow" in name or "statement_of_work" in name or "statement-of-work" in name:
        return "SOW"
    if "contractor" in name:
        return "CONTRACTOR_AGREEMENT"
    if "employ" in name:
        return "EMPLOYMENT"
    if "agency" in name:
        return "AGENCY_AGREEMENT"
    if "property" in name:
        return "PROPERTY_MANAGEMENT"
    if "purchase" in name:
        return "PURCHASE_AGREEMENT"
    if "msa" in name or "master" in name:
        return "MSA"
    return "SERVICE_AGREEMENT"


def _display_name_from_filename(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    base = base.replace("_", " ").replace("-", " ").strip()
    base = re.sub(r"\s+", " ", base)
    return base.title() if base else "Template"


def _sanitize_filename(name: str) -> str:
    base = os.path.basename(name).strip()
    base = base.replace("\\", "").replace("/", "")
    base = re.sub(r"[^A-Za-z0-9 _.-]+", "", base)
    base = re.sub(r"\s+", "_", base).strip("_")
    if not base.lower().endswith(".txt"):
        base = f"{base}.txt" if base else "New_Template.txt"
    return base


class TemplateFilesView(APIView):
    """Filesystem-backed templates (no DB).

    GET  /api/v1/templates/files/  -> list templates in CLM_Backend/templates
    POST /api/v1/templates/files/  -> create a new .txt template file (auth required)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        templates_dir = _templates_dir()
        if not os.path.isdir(templates_dir):
            return Response(
                {"success": True, "count": 0, "results": [], "message": "Templates directory not found"},
                status=status.HTTP_200_OK,
            )

        files = [f for f in os.listdir(templates_dir) if f.lower().endswith(".txt")]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(templates_dir, f)), reverse=True)

        results = []
        for filename in files:
            path = os.path.join(templates_dir, filename)
            meta = _read_template_meta(path)

            try:
                mtime = timezone.datetime.fromtimestamp(
                    os.path.getmtime(path), tz=timezone.get_current_timezone()
                )
                ctime = timezone.datetime.fromtimestamp(
                    os.path.getctime(path), tz=timezone.get_current_timezone()
                )
            except Exception:
                mtime = timezone.now()
                ctime = timezone.now()

            results.append(
                {
                    "id": filename,
                    "filename": filename,
                    "name": _display_name_from_filename(filename),
                    "contract_type": _infer_template_type(filename),
                    "status": "active",
                    "created_at": ctime.isoformat(),
                    "updated_at": mtime.isoformat(),
                    "created_by_id": meta.get("created_by_id"),
                    "created_by_email": meta.get("created_by_email"),
                    "description": meta.get("description") or "",
                }
            )

        return Response({"success": True, "count": len(results), "results": results}, status=status.HTTP_200_OK)

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        filename = (request.data.get("filename") or "").strip()
        description = (request.data.get("description") or "").strip()
        content = request.data.get("content")

        if content is None:
            return Response({"success": False, "error": "content is required"}, status=status.HTTP_400_BAD_REQUEST)

        proposed = filename or name or "New Template"
        safe = _sanitize_filename(proposed)

        templates_dir = _templates_dir()
        os.makedirs(templates_dir, exist_ok=True)

        path = os.path.join(templates_dir, safe)
        if os.path.exists(path):
            return Response(
                {"success": False, "error": "A template with that filename already exists", "filename": safe},
                status=status.HTTP_409_CONFLICT,
            )

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)

        now = timezone.now().isoformat()
        created_by_id = getattr(request.user, "user_id", None)
        created_by_email = getattr(request.user, "email", None)

        _write_template_meta(
            path,
            {
                "created_by_id": str(created_by_id) if created_by_id else None,
                "created_by_email": created_by_email,
                "description": description,
                "created_at": now,
                "updated_at": now,
            },
        )

        return Response(
            {
                "success": True,
                "template": {
                    "id": safe,
                    "filename": safe,
                    "name": _display_name_from_filename(safe),
                    "contract_type": _infer_template_type(safe),
                    "status": "active",
                    "created_at": now,
                    "updated_at": now,
                    "created_by_id": str(created_by_id) if created_by_id else None,
                    "created_by_email": created_by_email,
                    "description": description,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class TemplateMyFilesView(APIView):
    """GET /api/v1/templates/files/mine/ -> templates created by the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates_dir = _templates_dir()
        if not os.path.isdir(templates_dir):
            return Response(
                {"success": True, "count": 0, "results": [], "message": "Templates directory not found"},
                status=status.HTTP_200_OK,
            )

        user_id = getattr(request.user, "user_id", None)
        user_id_str = str(user_id) if user_id else None
        email = getattr(request.user, "email", None)

        files = [f for f in os.listdir(templates_dir) if f.lower().endswith(".txt")]
        files.sort(key=lambda f: os.path.getmtime(os.path.join(templates_dir, f)), reverse=True)

        results = []
        for filename in files:
            path = os.path.join(templates_dir, filename)
            meta = _read_template_meta(path)
            if not meta:
                continue

            meta_created_by_id = meta.get("created_by_id")
            meta_created_by_id_str = str(meta_created_by_id) if meta_created_by_id else None

            if user_id_str and meta_created_by_id_str == user_id_str:
                pass
            elif email and meta.get("created_by_email") == email:
                pass
            else:
                continue

            try:
                mtime = timezone.datetime.fromtimestamp(
                    os.path.getmtime(path), tz=timezone.get_current_timezone()
                )
                ctime = timezone.datetime.fromtimestamp(
                    os.path.getctime(path), tz=timezone.get_current_timezone()
                )
            except Exception:
                mtime = timezone.now()
                ctime = timezone.now()

            results.append(
                {
                    "id": filename,
                    "filename": filename,
                    "name": _display_name_from_filename(filename),
                    "contract_type": _infer_template_type(filename),
                    "status": "active",
                    "created_at": ctime.isoformat(),
                    "updated_at": mtime.isoformat(),
                    "created_by_id": meta.get("created_by_id"),
                    "created_by_email": meta.get("created_by_email"),
                    "description": meta.get("description") or "",
                }
            )

        return Response({"success": True, "count": len(results), "results": results}, status=status.HTTP_200_OK)


class TemplateFileContentView(APIView):
    """GET /api/v1/templates/files/content/<filename>/ -> exact raw .txt content."""

    permission_classes = [AllowAny]

    def get(self, request, filename: str):
        safe = _sanitize_filename(filename)
        templates_dir = _templates_dir()
        path = os.path.join(templates_dir, safe)

        if not os.path.exists(path):
            return Response(
                {"success": False, "error": "Template file not found", "filename": safe},
                status=status.HTTP_404_NOT_FOUND,
            )

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return Response(
            {
                "success": True,
                "filename": safe,
                "name": _display_name_from_filename(safe),
                "template_type": _infer_template_type(safe),
                "content": content,
                "size": os.path.getsize(path),
            },
            status=status.HTTP_200_OK,
        )


US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]


def _extract_placeholders(raw_text: str) -> list[str]:
    rx = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")
    return sorted({m.group(1).strip() for m in rx.finditer(raw_text) if m.group(1)})


def _schema_for_contract_type(contract_type: str) -> list[dict]:
    ct = (contract_type or "").upper()

    if ct == "NDA":
        return [
            {
                "title": "Party Details",
                "fields": [
                    {"key": "disclosing_party_name", "label": "Company Name (Disclosing Party)", "type": "text", "required": True},
                    {"key": "receiving_party_name", "label": "Counterparty Name (Receiving Party)", "type": "text", "required": True},
                ],
            },
            {
                "title": "Agreement Terms",
                "fields": [
                    {"key": "effective_date", "label": "Effective Date", "type": "date", "required": True},
                    {"key": "jurisdiction_state", "label": "Jurisdiction State", "type": "select", "required": True, "options": US_STATES},
                    {"key": "confidentiality_duration_years", "label": "Confidentiality Duration (Years)", "type": "number", "required": True},
                    {"key": "breach_penalty_amount", "label": "Breach Penalty Amount ($)", "type": "number", "required": False},
                ],
            },
        ]

    if ct == "MSA":
        return [
            {
                "title": "Party Details",
                "fields": [
                    {"key": "client_name", "label": "Client Company Name", "type": "text", "required": True},
                    {"key": "service_provider_name", "label": "Service Provider Name", "type": "text", "required": True},
                ],
            },
            {
                "title": "Agreement Terms",
                "fields": [
                    {"key": "effective_date", "label": "Effective Date", "type": "date", "required": True},
                    {"key": "governing_law_state", "label": "Governing Law (State)", "type": "select", "required": True, "options": US_STATES},
                    {"key": "payment_terms_days", "label": "Payment Terms (Days)", "type": "number", "required": False},
                    {"key": "liability_cap_amount", "label": "Liability Cap Amount ($)", "type": "number", "required": False},
                ],
            },
        ]

    if ct in {"SOW", "STATEMENT_OF_WORK"}:
        return [
            {
                "title": "Party Details",
                "fields": [
                    {"key": "client_name", "label": "Client Company Name", "type": "text", "required": True},
                    {"key": "provider_name", "label": "Provider Name", "type": "text", "required": True},
                ],
            },
            {
                "title": "Project Terms",
                "fields": [
                    {"key": "project_name", "label": "Project Name", "type": "text", "required": True},
                    {"key": "start_date", "label": "Start Date", "type": "date", "required": True},
                    {"key": "end_date", "label": "End Date", "type": "date", "required": False},
                    {"key": "payment_amount", "label": "Payment Amount ($)", "type": "number", "required": False},
                ],
            },
        ]

    if ct in {"CONTRACTOR_AGREEMENT", "EMPLOYMENT"}:
        return [
            {
                "title": "Party Details",
                "fields": [
                    {"key": "company_name", "label": "Company Name", "type": "text", "required": True},
                    {"key": "contractor_name", "label": "Contractor Name", "type": "text", "required": True},
                ],
            },
            {
                "title": "Engagement Terms",
                "fields": [
                    {"key": "start_date", "label": "Start Date", "type": "date", "required": True},
                    {"key": "end_date", "label": "End Date", "type": "date", "required": False},
                    {"key": "compensation_amount", "label": "Compensation Amount ($)", "type": "number", "required": False},
                    {"key": "termination_notice_days", "label": "Termination Notice (Days)", "type": "number", "required": False},
                ],
            },
        ]

    # Default schema: derive from placeholders on the frontend
    return [
        {
            "title": "Data Entry",
            "fields": [],
        }
    ]


class TemplateFileSchemaView(APIView):
    """GET /api/v1/templates/files/schema/<filename>/ -> required fields + clause/constraint UI metadata."""

    permission_classes = [AllowAny]

    def get(self, request, filename: str):
        safe = _sanitize_filename(filename)
        templates_dir = _templates_dir()
        path = os.path.join(templates_dir, safe)

        if not os.path.exists(path):
            return Response(
                {"success": False, "error": "Template file not found", "filename": safe},
                status=status.HTTP_404_NOT_FOUND,
            )

        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        template_type = _infer_template_type(safe)
        placeholders = _extract_placeholders(raw_text)
        sections = _schema_for_contract_type(template_type)

        # Mark which schema fields are actually present in the template as placeholders
        placeholder_set = set(placeholders)
        for section in sections:
            for field in section.get("fields", []):
                key = field.get("key")
                field["in_template"] = bool(key and key in placeholder_set)

        return Response(
            {
                "success": True,
                "filename": safe,
                "name": _display_name_from_filename(safe),
                "template_type": template_type,
                "placeholders": placeholders,
                "sections": sections,
                "clauses_ui": {
                    "allow_library_selection": True,
                    "allow_custom_clauses": True,
                    "allow_constraints": True,
                },
            },
            status=status.HTTP_200_OK,
        )
