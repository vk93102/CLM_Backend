import json
import os
import re
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from contracts.models import TemplateFile


def _infer_template_type(filename: str) -> str:
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


def _display_name_from_filename(filename: str) -> str:
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


class Command(BaseCommand):
    help = 'Import legacy filesystem .txt templates from BASE_DIR/templates into the TemplateFile DB table.'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing DB templates with filesystem content')

    def handle(self, *args, **options):
        overwrite = bool(options.get('overwrite'))
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')

        if not os.path.isdir(templates_dir):
            self.stdout.write(self.style.WARNING(f'Templates directory not found: {templates_dir}'))
            return

        files = [f for f in os.listdir(templates_dir) if f.lower().endswith('.txt')]
        files.sort()

        created = 0
        updated = 0
        skipped = 0
        errors = 0

        for filename in files:
            path = os.path.join(templates_dir, filename)
            meta = _read_meta(f'{path}.meta.json')

            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'Failed to read {filename}: {e}'))
                continue

            tenant_id = _parse_uuid(meta.get('tenant_id'))
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
                'tenant_id': tenant_id,
                'name': _display_name_from_filename(filename),
                'contract_type': _infer_template_type(filename),
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

            existing = TemplateFile.objects.filter(filename=filename).first()
            if existing and not overwrite:
                skipped += 1
                continue

            try:
                obj, was_created = TemplateFile.objects.update_or_create(
                    filename=filename,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

                # Best-effort preserve historical timestamps from meta.json
                created_at = _parse_dt(meta.get('created_at'))
                updated_at = _parse_dt(meta.get('updated_at'))
                if created_at or updated_at:
                    TemplateFile.objects.filter(id=obj.id).update(
                        created_at=created_at or obj.created_at,
                        updated_at=updated_at or obj.updated_at,
                    )
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'Failed to upsert {filename}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'Import complete: created={created}, updated={updated}, skipped={skipped}, errors={errors}'
        ))
