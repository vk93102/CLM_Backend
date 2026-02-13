import json
import os
import re
import uuid

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from contracts.models import TemplateFile
from contracts.utils.template_files_db import get_or_import_template_from_filesystem


def _template_entity_uuid(filename: str) -> uuid.UUID:
    # Deterministic UUID so search results can map back to a template file.
    # Keep stable across restarts.
    return uuid.uuid5(uuid.NAMESPACE_URL, f"clm.template_file:{filename}")


def _best_effort_index_template_for_tenant(*, tenant_id: uuid.UUID, filename: str) -> None:
    """Index a template file into SearchIndexModel for the given tenant."""
    try:
        from search.models import SearchIndexModel
        from search.services import SearchIndexingService

        tmpl = TemplateFile.objects.filter(filename=filename).first()
        if not tmpl:
            return

        try:
            updated_at_epoch = float(tmpl.updated_at.timestamp()) if tmpl.updated_at else None
        except Exception:
            updated_at_epoch = None
        try:
            size = len((tmpl.content or '').encode('utf-8'))
        except Exception:
            size = None

        entity_id = _template_entity_uuid(filename)
        existing = SearchIndexModel.objects.filter(
            tenant_id=tenant_id,
            entity_type='template',
            entity_id=entity_id,
        ).first()

        existing_md = (existing.metadata or {}) if existing else {}
        if (
            isinstance(existing_md, dict)
            and updated_at_epoch is not None
            and existing_md.get('source_updated_at_epoch') == updated_at_epoch
            and size is not None
            and existing_md.get('source_size') == size
        ):
            return

        content = tmpl.content or ''

        SearchIndexingService.create_index(
            entity_type='template',
            entity_id=str(entity_id),
            title=(tmpl.name or _display_name_from_filename(filename)),
            content=(content or '')[:20000],
            tenant_id=str(tenant_id),
            keywords=[tmpl.contract_type or _infer_template_type(filename)],
            metadata={
                'source': 'template_files_db',
                'filename': filename,
                'source_updated_at_epoch': updated_at_epoch,
                'source_size': size,
            },
        )
    except Exception:
        return


def _template_queryset_for_request(request):
    """Templates visible to the current request.

    Backward-compatible behavior: the legacy filesystem endpoints were public and
    returned all templates regardless of authentication, so we keep the DB-backed
    equivalents consistent.
    """
    return TemplateFile.objects.all()


def _get_visible_template(request, filename: str) -> tuple[str, TemplateFile | None]:
    safe = _sanitize_filename(filename)
    tmpl = _template_queryset_for_request(request).filter(filename=safe).first()
    if not tmpl:
        # Transitional compatibility: auto-import from filesystem if present.
        try:
            tenant_id = None
            user = getattr(request, 'user', None)
            if getattr(user, 'is_authenticated', False):
                tenant_id = getattr(user, 'tenant_id', None)
            tmpl = get_or_import_template_from_filesystem(filename=safe, tenant_id=tenant_id)
        except Exception:
            tmpl = None
    return safe, tmpl


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
    """DB-backed templates.

    GET  /api/v1/templates/files/  -> list templates from DB
    POST /api/v1/templates/files/  -> create a new text template in DB (auth required)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        templates = list(_template_queryset_for_request(request).order_by('-updated_at'))

        # Transitional compatibility: if DB is empty, import legacy filesystem templates.
        if not templates:
            try:
                tenant_id = None
                if getattr(request.user, 'is_authenticated', False):
                    tenant_id = getattr(request.user, 'tenant_id', None)

                fs_dir = os.path.join(settings.BASE_DIR, 'templates')
                if os.path.isdir(fs_dir):
                    for fn in os.listdir(fs_dir):
                        if isinstance(fn, str) and fn.lower().endswith('.txt'):
                            get_or_import_template_from_filesystem(filename=fn, tenant_id=tenant_id)

                templates = list(_template_queryset_for_request(request).order_by('-updated_at'))
            except Exception:
                pass

        # Best-effort: keep the tenant's template search index warm.
        try:
            if getattr(request.user, 'is_authenticated', False) and getattr(request.user, 'tenant_id', None):
                tenant_id = request.user.tenant_id
                # Keep it bounded; index the most-recent N.
                for tmpl in templates[:50]:
                    _best_effort_index_template_for_tenant(tenant_id=tenant_id, filename=tmpl.filename)
        except Exception:
            pass

        results = []
        for tmpl in templates:
            results.append(
                {
                    "id": tmpl.filename,
                    "filename": tmpl.filename,
                    "name": tmpl.name or _display_name_from_filename(tmpl.filename),
                    "contract_type": tmpl.contract_type or _infer_template_type(tmpl.filename),
                    "status": tmpl.status or "active",
                    "created_at": (tmpl.created_at or timezone.now()).isoformat(),
                    "updated_at": (tmpl.updated_at or timezone.now()).isoformat(),
                    "created_by_id": str(tmpl.created_by_id) if tmpl.created_by_id else None,
                    "created_by_email": tmpl.created_by_email,
                    "description": tmpl.description or "",
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

        if TemplateFile.objects.filter(filename=safe).exists():
            return Response(
                {"success": False, "error": "A template with that filename already exists", "filename": safe},
                status=status.HTTP_409_CONFLICT,
            )

        created_by_id = getattr(request.user, "user_id", None)
        created_by_email = getattr(request.user, "email", None)
        tenant_id = getattr(request.user, 'tenant_id', None)

        tmpl = TemplateFile.objects.create(
            tenant_id=tenant_id,
            filename=safe,
            name=_display_name_from_filename(safe),
            contract_type=_infer_template_type(safe),
            description=description,
            status='active',
            content=content,
            created_by_id=created_by_id,
            created_by_email=created_by_email,
            meta={
                'created_from': 'api',
            },
        )

        now = (tmpl.created_at or timezone.now()).isoformat()

        # Best-effort: index new template for semantic/keyword search.
        try:
            if tenant_id:
                _best_effort_index_template_for_tenant(tenant_id=tenant_id, filename=safe)
        except Exception:
            pass

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
                    "updated_at": (tmpl.updated_at or timezone.now()).isoformat(),
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
        user_id = getattr(request.user, "user_id", None)
        user_id_str = str(user_id) if user_id else None
        email = getattr(request.user, "email", None)

        qs = _template_queryset_for_request(request)
        if user_id_str or email:
            q = Q()
            if user_id_str:
                q |= Q(created_by_id=user_id)
            if email:
                q |= Q(created_by_email=email)
            qs = qs.filter(q)

        results = []
        for tmpl in qs.order_by('-updated_at'):
            results.append(
                {
                    "id": tmpl.filename,
                    "filename": tmpl.filename,
                    "name": tmpl.name or _display_name_from_filename(tmpl.filename),
                    "contract_type": tmpl.contract_type or _infer_template_type(tmpl.filename),
                    "status": tmpl.status or "active",
                    "created_at": (tmpl.created_at or timezone.now()).isoformat(),
                    "updated_at": (tmpl.updated_at or timezone.now()).isoformat(),
                    "created_by_id": str(tmpl.created_by_id) if tmpl.created_by_id else None,
                    "created_by_email": tmpl.created_by_email,
                    "description": tmpl.description or "",
                }
            )

        return Response({"success": True, "count": len(results), "results": results}, status=status.HTTP_200_OK)


class TemplateFileContentView(APIView):
    """GET /api/v1/templates/files/content/<filename>/ -> exact raw .txt content."""

    permission_classes = [AllowAny]

    def get(self, request, filename: str):
        safe, tmpl = _get_visible_template(request, filename)
        if not tmpl:
            return Response(
                {"success": False, "error": "Template file not found", "filename": safe},
                status=status.HTTP_404_NOT_FOUND,
            )

        content = tmpl.content or ''

        return Response(
            {
                "success": True,
                "filename": safe,
                "name": tmpl.name or _display_name_from_filename(safe),
                "template_type": tmpl.contract_type or _infer_template_type(safe),
                "content": content,
                "size": len((content or '').encode('utf-8')),
            },
            status=status.HTTP_200_OK,
        )


class TemplateFileDeleteView(APIView):
    """DELETE /api/v1/templates/files/<filename>/ -> delete template created by current user."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, filename: str):
        safe = _sanitize_filename(filename)

        tmpl = TemplateFile.objects.filter(filename=safe).first()
        if not tmpl:
            return Response(
                {"success": False, "error": "Template file not found", "filename": safe},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        user_id = getattr(user, 'user_id', None)
        user_uuid = None
        try:
            if user_id:
                user_uuid = uuid.UUID(str(user_id))
        except Exception:
            user_uuid = None
        user_email = (getattr(user, 'email', None) or '').strip().lower()
        tenant_id_raw = getattr(user, 'tenant_id', None)
        tenant_uuid = None
        try:
            if tenant_id_raw:
                tenant_uuid = uuid.UUID(str(tenant_id_raw))
        except Exception:
            tenant_uuid = None

        tmpl_email = (tmpl.created_by_email or '').strip().lower()
        is_owner = bool(
            (user_uuid and tmpl.created_by_id and tmpl.created_by_id == user_uuid)
            or (user_email and tmpl_email and tmpl_email == user_email)
        )

        # Tenant isolation: only allow deleting templates within the user's tenant.
        # (Global templates are treated as non-deletable unless you are the creator.)
        same_tenant = (tmpl.tenant_id is None) or (tenant_uuid and tmpl.tenant_id == tenant_uuid)

        if not is_owner or not same_tenant:
            return Response(
                {"success": False, "error": "You can only delete templates you created."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Best-effort: remove from search index.
        try:
            if tenant_uuid:
                from search.services import SearchIndexingService

                SearchIndexingService.delete_index(entity_id=str(_template_entity_uuid(safe)))
        except Exception:
            pass

        tmpl.delete()
        return Response({"success": True, "filename": safe}, status=status.HTTP_200_OK)


def _default_signature_fields_config() -> dict:
    return {
        "fields": [
            {
                "label": "Primary Signature",
                "type": "signature",
                "page_number": 1,
                "position": {"x": 10, "y": 80, "width": 30, "height": 8},
                "required": True,
                "recipient_index": 0,
            }
        ],
        "auto_stack": True,
        "stack_spacing": 12,
        "source": "default",
    }


def _validate_signature_fields_config(cfg: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(cfg, dict):
        return ["Configuration must be a JSON object"]

    fields = cfg.get("fields", [])
    if not isinstance(fields, list):
        return ["fields must be an array"]

    for idx, field in enumerate(fields):
        if not isinstance(field, dict):
            errors.append(f"Field {idx}: must be an object")
            continue

        if field.get("type") != "signature":
            errors.append(f"Field {idx}: type must be 'signature'")

        try:
            page_num = int(field.get("page_number") or 1)
            if page_num < 1:
                errors.append(f"Field {idx}: page_number must be >= 1")
        except (ValueError, TypeError):
            errors.append(f"Field {idx}: page_number must be an integer")

        try:
            recipient_index = int(field.get("recipient_index"))
            if recipient_index < 0:
                errors.append(f"Field {idx}: recipient_index must be >= 0")
        except (ValueError, TypeError):
            errors.append(f"Field {idx}: recipient_index must be an integer")

        position = field.get("position")
        if not isinstance(position, dict):
            errors.append(f"Field {idx}: position is required and must be an object")
            continue

        for coord in ["x", "y", "width", "height"]:
            if coord not in position:
                errors.append(f"Field {idx}: position.{coord} is required")
                continue
            try:
                val = float(position[coord])
                if not (0 <= val <= 100):
                    errors.append(f"Field {idx}: position.{coord} must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append(f"Field {idx}: position.{coord} must be a number")

    return errors


class TemplateFileSignatureFieldsConfigView(APIView):
    """Get/update Firma signature field configuration stored in template meta.

    GET  /api/v1/templates/files/signature-fields-config/<filename>/
    PUT  /api/v1/templates/files/signature-fields-config/<filename>/

    Stored in DB: TemplateFile.signature_fields_config
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, filename: str):
        safe, tmpl = _get_visible_template(request, filename)
        if not tmpl:
            return Response({"success": False, "error": "Template file not found", "filename": safe}, status=404)

        cfg = tmpl.signature_fields_config
        if not isinstance(cfg, dict) or not isinstance(cfg.get("fields"), list):
            cfg = _default_signature_fields_config()
            source = "default"
        else:
            source = "template_db"

        return Response(
            {
                "success": True,
                "filename": safe,
                "config": cfg,
                "source": source,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, filename: str):
        safe, tmpl = _get_visible_template(request, filename)
        if not tmpl:
            return Response({"success": False, "error": "Template file not found", "filename": safe}, status=404)

        cfg = request.data
        errors = _validate_signature_fields_config(cfg)
        if errors:
            return Response({"success": False, "error": "Invalid configuration", "validation_errors": errors}, status=400)

        cfg_to_save = {
            "fields": cfg.get("fields", []),
            "auto_stack": bool(cfg.get("auto_stack", True)),
            "stack_spacing": int(cfg.get("stack_spacing", 12)),
            "source": "template_editor",
        }

        tmpl.signature_fields_config = cfg_to_save
        tmpl.signature_fields_updated_at = timezone.now()
        tmpl.signature_fields_updated_by_id = getattr(request.user, "user_id", None)
        tmpl.signature_fields_updated_by_email = getattr(request.user, "email", None)
        tmpl.save(update_fields=[
            'signature_fields_config',
            'signature_fields_updated_at',
            'signature_fields_updated_by_id',
            'signature_fields_updated_by_email',
            'updated_at',
        ])

        return Response(
            {"success": True, "filename": safe, "config": tmpl.signature_fields_config},
            status=status.HTTP_200_OK,
        )


class TemplateFileDragSignaturePositionsView(APIView):
    """Save signature positions from drag-and-drop UI into template meta.

    POST /api/v1/templates/files/drag-signature-positions/<filename>/
    Body: {"positions": [{"recipient_index":0,"page_number":1,"position":{"x":10,"y":80,"width":30,"height":8}}]}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, filename: str):
        safe, tmpl = _get_visible_template(request, filename)
        if not tmpl:
            return Response({"success": False, "error": "Template file not found", "filename": safe}, status=404)

        positions = request.data.get("positions", [])
        if not isinstance(positions, list):
            return Response({"success": False, "error": "positions must be an array"}, status=400)

        fields = []
        for idx, pos_data in enumerate(positions):
            if not isinstance(pos_data, dict):
                return Response({"success": False, "error": f"Position {idx}: must be an object"}, status=400)
            if "recipient_index" not in pos_data:
                return Response({"success": False, "error": f"Position {idx}: recipient_index is required"}, status=400)
            if "page_number" not in pos_data:
                return Response({"success": False, "error": f"Position {idx}: page_number is required"}, status=400)
            if "position" not in pos_data or not isinstance(pos_data.get("position"), dict):
                return Response({"success": False, "error": f"Position {idx}: position must be an object"}, status=400)

            pos = pos_data["position"]
            for key in ["x", "y", "width", "height"]:
                if key not in pos:
                    return Response({"success": False, "error": f"Position {idx}: position.{key} is required"}, status=400)
                if not isinstance(pos[key], (int, float)):
                    return Response({"success": False, "error": f"Position {idx}: position.{key} must be a number"}, status=400)

            try:
                recipient_index = int(pos_data["recipient_index"])
                page_number = int(pos_data["page_number"])
            except (ValueError, TypeError):
                return Response({"success": False, "error": f"Position {idx}: recipient_index/page_number must be integers"}, status=400)

            fields.append(
                {
                    "label": f"Signature {recipient_index + 1}",
                    "type": "signature",
                    "page_number": page_number,
                    "position": {"x": float(pos["x"]), "y": float(pos["y"]), "width": float(pos["width"]), "height": float(pos["height"])},
                    "required": True,
                    "recipient_index": recipient_index,
                }
            )

        cfg = {"fields": fields, "auto_stack": False, "source": "drag_drop_ui", "stack_spacing": 12}
        errors = _validate_signature_fields_config(cfg)
        if errors:
            return Response({"success": False, "error": "Invalid positions", "validation_errors": errors}, status=400)

        tmpl.signature_fields_config = cfg
        tmpl.signature_fields_updated_at = timezone.now()
        tmpl.signature_fields_updated_by_id = getattr(request.user, "user_id", None)
        tmpl.signature_fields_updated_by_email = getattr(request.user, "email", None)
        tmpl.save(update_fields=[
            'signature_fields_config',
            'signature_fields_updated_at',
            'signature_fields_updated_by_id',
            'signature_fields_updated_by_email',
            'updated_at',
        ])

        return Response({"success": True, "filename": safe, "fields_count": len(fields), "config": cfg}, status=status.HTTP_200_OK)


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
        safe, tmpl = _get_visible_template(request, filename)
        if not tmpl:
            return Response(
                {"success": False, "error": "Template file not found", "filename": safe},
                status=status.HTTP_404_NOT_FOUND,
            )

        raw_text = tmpl.content or ''

        template_type = tmpl.contract_type or _infer_template_type(safe)
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
                "name": tmpl.name or _display_name_from_filename(safe),
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
