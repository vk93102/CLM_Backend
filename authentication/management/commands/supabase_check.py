from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Verify Supabase-only DB connectivity and Supabase API env vars"

    def handle(self, *args, **options):
        db = settings.DATABASES.get("default", {})
        host = db.get("HOST")
        port = db.get("PORT")
        name = db.get("NAME")
        engine = db.get("ENGINE")
        sslmode = (db.get("OPTIONS") or {}).get("sslmode")
        user = db.get("USER")

        self.stdout.write("DB settings (sanitized):")
        self.stdout.write(f"  ENGINE: {engine}")
        self.stdout.write(f"  HOST:   {host}")
        self.stdout.write(f"  PORT:   {port}")
        self.stdout.write(f"  NAME:   {name}")
        self.stdout.write(f"  SSL:    {sslmode}")

        if user:
            # Avoid printing secrets; just show a prefix.
            safe_user = str(user)
            if len(safe_user) > 10:
                safe_user = safe_user[:10] + "..."
            self.stdout.write(f"  USER:   {safe_user}")

        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("select 1")
                row = cursor.fetchone()
            self.stdout.write(self.style.SUCCESS(f"DB connectivity: OK (select 1 => {row})"))
        except Exception as exc:
            raise SystemExit(self.style.ERROR(f"DB connectivity: FAILED ({exc})"))

        supabase_url = (getattr(settings, "SUPABASE_URL", None) or "").strip()
        supabase_key = (getattr(settings, "SUPABASE_KEY", None) or "").strip()
        supabase_anon = (getattr(settings, "SUPABASE_ANON_KEY", None) or "").strip()

        self.stdout.write("Supabase API env (sanitized):")
        self.stdout.write(f"  SUPABASE_URL set: {bool(supabase_url)}")
        self.stdout.write(f"  SUPABASE_KEY set: {bool(supabase_key)}")
        self.stdout.write(f"  SUPABASE_ANON_KEY set: {bool(supabase_anon)}")

        if supabase_url and not supabase_url.startswith("https://"):
            raise SystemExit(self.style.ERROR("SUPABASE_URL should start with https://"))

        # If we're using the Supabase pooler host, ensure the DB username matches the project ref.
        # Pooler typically requires user format: postgres.<project_ref>
        try:
            if host and "pooler.supabase.com" in str(host) and supabase_url:
                ref = urlparse(supabase_url).hostname.split(".")[0]
                if ref and user and str(user).startswith("postgres.") and not str(user).endswith("." + ref):
                    raise SystemExit(
                        self.style.ERROR(
                            "DB_USER does not match SUPABASE_URL project ref. "
                            f"Expected suffix '.{ref}' for pooler connections."
                        )
                    )
        except SystemExit:
            raise
        except Exception:
            # Non-fatal; don't block deployments on parsing issues.
            pass

        self.stdout.write(self.style.SUCCESS("Supabase check: OK"))
