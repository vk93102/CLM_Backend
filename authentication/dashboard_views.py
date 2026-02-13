from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit_logs.models import AuditLogModel
from ai.models import DraftGenerationTask
from calendar_events.models import CalendarEvent
from contracts.models import Contract, ESignatureContract, FirmaSignatureContract
from reviews.models import ReviewContract


class DashboardInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tenant_id = getattr(user, 'tenant_id', None)
        user_id = getattr(user, 'user_id', None)

        if not tenant_id or not user_id:
            return Response({'success': False, 'error': 'Invalid user context'}, status=400)

        now = timezone.now()
        since_30d = now - timedelta(days=30)
        since_14d = now - timedelta(days=14)
        since_180d = now - timedelta(days=180)

        # Derive usage counts from first-class data so the dashboard remains
        # informative even when AuditLog coverage is partial.
        review_count_30d = ReviewContract.objects.filter(
            tenant_id=tenant_id,
            created_by=user_id,
            created_at__gte=since_30d,
        ).count()

        upload_count_30d = 0
        try:
            from repository.models import Document

            upload_count_30d = Document.objects.filter(
                tenant_id=tenant_id,
                uploaded_by_id=user_id,
                uploaded_at__gte=since_30d,
            ).count()
        except Exception:
            upload_count_30d = 0

        # -------------------- Feature usage (Audit logs) --------------------
        feature_rows = (
            AuditLogModel.objects.filter(tenant_id=tenant_id, user_id=user_id, created_at__gte=since_30d)
            .values('entity_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        usage_map: dict[str, int] = {}
        for r in feature_rows:
            key = (r.get('entity_type') or 'unknown')
            usage_map[key] = int(r.get('count') or 0)

        # Ensure canonical keys used by the frontend exist.
        usage_map['review'] = max(int(usage_map.get('review', 0) or 0), int(review_count_30d))
        usage_map['upload'] = max(int(usage_map.get('upload', 0) or 0), int(upload_count_30d))

        feature_usage = [
            {'key': 'review', 'count': int(usage_map.get('review', 0) or 0)},
            {'key': 'upload', 'count': int(usage_map.get('upload', 0) or 0)},
        ]

        # Add remaining audit-derived keys (bounded).
        for key, count in sorted(
            ((k, v) for k, v in usage_map.items() if k not in {'review', 'upload'}),
            key=lambda kv: kv[1],
            reverse=True,
        ):
            feature_usage.append({'key': key, 'count': int(count)})
            if len(feature_usage) >= 12:
                break

        # -------------------- Activity trend (last 14 days) --------------------
        day_rows = (
            AuditLogModel.objects.filter(tenant_id=tenant_id, user_id=user_id, created_at__gte=since_14d)
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        day_map = {r['day'].date().isoformat(): int(r['count']) for r in day_rows if r.get('day')}
        activity_last_14_days = []
        for i in range(13, -1, -1):
            d = (now - timedelta(days=i)).date().isoformat()
            activity_last_14_days.append({'date': d, 'count': int(day_map.get(d, 0))})

        # -------------------- Contracts by type --------------------
        contract_rows = (
            Contract.objects.filter(tenant_id=tenant_id, created_by=user_id, created_at__gte=since_180d)
            .values('contract_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        contract_types = []
        for r in contract_rows:
            raw = (r.get('contract_type') or '').strip()
            contract_types.append({'type': raw or 'Unspecified', 'count': int(r.get('count') or 0)})

        # -------------------- AI usage (Draft generation tasks) --------------------
        ai_rows = (
            DraftGenerationTask.objects.filter(tenant_id=tenant_id, user_id=user_id, created_at__gte=since_180d)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        ai_status_map: dict[str, int] = {}
        for r in ai_rows:
            s = (r.get('status') or 'unknown')
            ai_status_map[s] = ai_status_map.get(s, 0) + int(r.get('count') or 0)

        # Review feature invokes AI (Gemini/Voyage) but does not currently create DraftGenerationTask rows.
        # Fold review pipeline counts into AI usage so the dashboard updates for real usage.
        review_ai_rows = (
            ReviewContract.objects.filter(tenant_id=tenant_id, created_by=user_id, created_at__gte=since_180d)
            .values('status')
            .annotate(count=Count('id'))
        )
        status_map = {
            'uploaded': 'pending',
            'processing': 'processing',
            'ready': 'completed',
            'failed': 'failed',
        }
        for r in review_ai_rows:
            raw = (r.get('status') or 'unknown')
            mapped = status_map.get(raw, 'unknown')
            ai_status_map[mapped] = ai_status_map.get(mapped, 0) + int(r.get('count') or 0)

        ai_by_status = [
            {'status': s, 'count': int(c)}
            for s, c in sorted(ai_status_map.items(), key=lambda kv: kv[1], reverse=True)
        ]

        # -------------------- Review stats --------------------
        review_rows = (
            ReviewContract.objects.filter(tenant_id=tenant_id, created_by=user_id, created_at__gte=since_180d)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        reviews_by_status = [
            {'status': (r.get('status') or 'unknown'), 'count': int(r.get('count') or 0)} for r in review_rows
        ]

        # -------------------- Calendar stats --------------------
        upcoming_end = now + timedelta(days=30)
        upcoming_30d = CalendarEvent.objects.filter(
            tenant_id=tenant_id,
            created_by=user_id,
            start_datetime__gte=now,
            start_datetime__lte=upcoming_end,
        ).count()

        calendar_rows = (
            CalendarEvent.objects.filter(tenant_id=tenant_id, created_by=user_id, start_datetime__gte=since_180d)
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        calendar_by_category = [
            {'category': (r.get('category') or 'unknown'), 'count': int(r.get('count') or 0)}
            for r in calendar_rows
        ]

        # -------------------- E-sign usage (Firma vs SignNow) --------------------
        # Note: these models do not store tenant_id directly; we filter via the linked contract.
        firma_qs = FirmaSignatureContract.objects.filter(
            contract__tenant_id=tenant_id,
            contract__created_by=user_id,
            created_at__gte=since_180d,
        )
        signnow_qs = ESignatureContract.objects.filter(
            contract__tenant_id=tenant_id,
            contract__created_by=user_id,
            created_at__gte=since_180d,
        )

        firma_total = firma_qs.count()
        signnow_total = signnow_qs.count()

        firma_status_rows = firma_qs.values('status').annotate(count=Count('id')).order_by('-count')
        signnow_status_rows = signnow_qs.values('status').annotate(count=Count('id')).order_by('-count')

        firma_by_status = [
            {'status': (r.get('status') or 'unknown'), 'count': int(r.get('count') or 0)}
            for r in firma_status_rows
        ]
        signnow_by_status = [
            {'status': (r.get('status') or 'unknown'), 'count': int(r.get('count') or 0)}
            for r in signnow_status_rows
        ]

        return Response(
            {
                'success': True,
                'window_days': 180,
                'feature_usage_30d': feature_usage,
                'activity_last_14_days': activity_last_14_days,
                'contract_types_180d': contract_types,
                'ai_tasks_by_status_180d': ai_by_status,
                'reviews_by_status_180d': reviews_by_status,
                'calendar_by_category_180d': calendar_by_category,
                'calendar_upcoming_30d': int(upcoming_30d),
                'esign_by_provider_180d': [
                    {'provider': 'firma', 'count': int(firma_total)},
                    {'provider': 'signnow', 'count': int(signnow_total)},
                ],
                'firma_by_status_180d': firma_by_status,
                'signnow_by_status_180d': signnow_by_status,
            }
        )
