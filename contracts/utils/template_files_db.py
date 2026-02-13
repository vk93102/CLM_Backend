import json
import os
import re
import uuid

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from contracts.models import TemplateFile


def sanitize_template_filename(name: str) -> str:
    base = os.path.basename(str(name or '').strip())
    base = base.replace('\\', '').replace('/', '')
    base = re.sub(r'[^A-Za-z0-9 _.-]+', '', base)
    base = re.sub(r'\s+', '_', base).strip('_')
    if not base.lower().endswith('.txt'):
        base = f'{base}.txt' if base else 'Template.txt'
    return base


def infer_template_type(filename: str) -> str:
    name = (filename or '').lower()
    if 'nda' in name:
        return 'NDA'
    if 'sow' in name or 'statement_of_work' in name or 'statement-of-work' in name:
        return 'SOW'
    if 'contractor' in name:
        return 'CONTRACTOR_AGREEMENT'
    if 'employ' in name:
        return 'EMPLOYMENT'
    if 'agency' in name:
        return 'AGENCY_AGREEMENT'
    if 'property' in name:
        return 'PROPERTY_MANAGEMENT'
    if 'purchase' in name:
        return 'PURCHASE_AGREEMENT'
    if 'msa' in name or 'master' in name:
        return 'MSA'
    return 'SERVICE_AGREEMENT'


def display_name_from_filename(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename or ''))[0]
    base = base.replace('_', ' ').replace('-', ' ').strip()
    base = re.sub(r'\s+', ' ', base)
    return base.title() if base else 'Template'


def _read_meta(meta_path: str) -> dict:
    if not meta_path or not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _parse_uuid(value):
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except Exception:
        return None


def _parse_dt(value):
    if not value:
        return None
    try:
        return timezone.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except Exception:
        return None


def get_template_for_tenant(*, filename: str, tenant_id=None) -> TemplateFile | None:
    safe = sanitize_template_filename(filename)
    qs = TemplateFile.objects.filter(filename=safe)
    if tenant_id:
        qs = qs.filter(Q(tenant_id=tenant_id) | Q(tenant_id__isnull=True))
    return qs.first()


def get_or_import_template_from_filesystem(*, filename: str, tenant_id=None) -> TemplateFile | None:
    """Best-effort: if the template isn't in DB yet, import it from BASE_DIR/templates."""
    safe = sanitize_template_filename(filename)

    existing = get_template_for_tenant(filename=safe, tenant_id=tenant_id)
    if existing:
        return existing

    path = os.path.join(settings.BASE_DIR, 'templates', safe)
    if not os.path.exists(path):
        return None

    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        content = ''

    meta = _read_meta(f'{path}.meta.json')

    meta_tenant_id = _parse_uuid(meta.get('tenant_id'))
    created_by_id = _parse_uuid(meta.get('created_by_id'))
    created_by_email = meta.get('created_by_email')
    description = meta.get('description')

    signature_cfg = meta.get('signature_fields_config')
    if not (isinstance(signature_cfg, dict) and isinstance(signature_cfg.get('fields'), list)):
        signature_cfg = {}

    signature_fields_updated_at = _parse_dt(meta.get('signature_fields_updated_at'))
    signature_fields_updated_by_id = _parse_uuid(meta.get('signature_fields_updated_by_id'))
    signature_fields_updated_by_email = meta.get('signature_fields_updated_by_email')

    defaults = {
        'tenant_id': meta_tenant_id,
        'name': display_name_from_filename(safe),
        'contract_type': infer_template_type(safe),
        'description': description or '',
        'status': 'active',
        'content': content or '',
        'created_by_id': created_by_id,
        'created_by_email': created_by_email,
        'signature_fields_config': signature_cfg,
        'signature_fields_updated_at': signature_fields_updated_at,
        'signature_fields_updated_by_id': signature_fields_updated_by_id,
        'signature_fields_updated_by_email': signature_fields_updated_by_email,
        'meta': meta or {},
    }

    try:
        obj, _ = TemplateFile.objects.get_or_create(filename=safe, defaults=defaults)

        # Best-effort preserve historical timestamps from meta.json
        created_at = _parse_dt(meta.get('created_at'))
        updated_at = _parse_dt(meta.get('updated_at'))
        if created_at or updated_at:
            TemplateFile.objects.filter(id=obj.id).update(
                created_at=created_at or obj.created_at,
                updated_at=updated_at or obj.updated_at,
            )

        return obj
    except Exception:
        # If there was a race, try a final read.
        return TemplateFile.objects.filter(filename=safe).first()
