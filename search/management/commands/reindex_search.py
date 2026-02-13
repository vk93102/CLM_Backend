from __future__ import annotations

import uuid

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Rebuild tenant search index for contracts and clauses"

    def add_arguments(self, parser):
        parser.add_argument("--tenant", required=True, help="Tenant UUID")
        parser.add_argument("--contracts", action="store_true", help="Index contracts")
        parser.add_argument("--clauses", action="store_true", help="Index clause library")
        parser.add_argument("--limit", type=int, default=0, help="Max items per type (0 = no limit)")
        parser.add_argument("--dry-run", action="store_true", help="Print what would be indexed")

    def handle(self, *args, **options):
        from contracts.models import Clause, Contract
        from search.services import SearchIndexingService

        tenant_raw = (options.get("tenant") or "").strip()
        try:
            tenant_id = uuid.UUID(tenant_raw)
        except Exception as e:
            raise SystemExit(f"Invalid --tenant UUID: {tenant_raw} ({e})")

        do_contracts = bool(options.get("contracts"))
        do_clauses = bool(options.get("clauses"))
        limit = int(options.get("limit") or 0)
        dry_run = bool(options.get("dry_run"))

        if not do_contracts and not do_clauses:
            do_contracts = True
            do_clauses = True

        total_indexed = 0

        if do_contracts:
            qs = Contract.objects.filter(tenant_id=tenant_id).order_by("-updated_at")
            if limit > 0:
                qs = qs[:limit]

            indexed = 0
            for c in qs:
                md = c.metadata or {}
                text = (md.get("rendered_text") or "").strip()
                if not text:
                    continue

                if dry_run:
                    self.stdout.write(f"[dry-run] contract {c.id} title={c.title!r}")
                    indexed += 1
                    continue

                SearchIndexingService.create_index(
                    entity_type="contract",
                    entity_id=str(c.id),
                    title=c.title or "Contract",
                    content=text,
                    tenant_id=str(tenant_id),
                    keywords=[x for x in [c.contract_type, c.status] if x],
                )
                indexed += 1

            total_indexed += indexed
            self.stdout.write(self.style.SUCCESS(f"Contracts indexed: {indexed}"))

        if do_clauses:
            qs = Clause.objects.filter(tenant_id=tenant_id).order_by("-updated_at")
            if limit > 0:
                qs = qs[:limit]

            indexed = 0
            for cl in qs:
                if dry_run:
                    self.stdout.write(f"[dry-run] clause {cl.id} name={cl.name!r}")
                    indexed += 1
                    continue

                SearchIndexingService.create_index(
                    entity_type="clause",
                    entity_id=str(cl.id),
                    title=cl.name or cl.clause_id or "Clause",
                    content=cl.content or "",
                    tenant_id=str(tenant_id),
                    keywords=[x for x in [cl.contract_type, cl.status] if x],
                )
                indexed += 1

            total_indexed += indexed
            self.stdout.write(self.style.SUCCESS(f"Clauses indexed: {indexed}"))

        self.stdout.write(self.style.SUCCESS(f"Total indexed: {total_indexed}"))
