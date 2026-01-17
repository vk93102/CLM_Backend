# AI Endpoints Setup & Deployment Guide

## Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Verify installations
python --version  # 3.11+
pip list | grep -E "django|celery|google-generativeai|voyageai"
redis-cli --version
```

### 2. Environment Variables
Add to `.env`:
```bash
# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Voyage AI (optional, falls back to semantic mock)
VOYAGE_API_KEY=your-voyage-ai-key

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

Get API keys:
- **Gemini**: https://aistudio.google.com/app/apikeys
- **Voyage AI**: https://www.voyageai.com/dashboard/api-keys

### 3. Start Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A clm_backend worker -l info --concurrency=2

# Terminal 3: Django Dev Server
python manage.py runserver

# Terminal 4: Celery Flower (optional, monitoring)
celery -A clm_backend flower
```

### 4. Initialize Anchor Clauses
```bash
# Initialize 14 anchor clauses with embeddings
python manage.py initialize_anchors

# Output:
# ✓ Created: Confidentiality (Legal)
# ✓ Created: Limitation of Liability (Legal)
# ...
# ✓ Initialization Complete!
#   Created: 14
#   Updated: 0
#   Failed: 0
#   Total Active Anchors: 14
```

### 5. Test Endpoints
```bash
# Get JWT token from your auth endpoint
export JWT_TOKEN="your-jwt-token"

# Test draft generation
bash test_ai_endpoints.sh
```

---

## Detailed Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt

# Add if missing:
pip install celery==5.3.6
pip install redis==5.0.1
pip install google-generativeai==0.5.4
pip install voyageai==0.3.0
pip install numpy==1.24.3
```

### Step 2: Configure Django

**clm_backend/settings.py** (already configured):
```python
# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')
```

**clm_backend/celery.py** (create if missing):
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

app = Celery('clm_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**clm_backend/__init__.py** (add):
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate

# Verify models created:
python manage.py dbshell
# \dt ai_*
# \dt repository_document*
```

### Step 4: Initialize Anchor Clauses

```bash
python manage.py initialize_anchors

# Verify in database:
python manage.py shell
>>> from ai.models import ClauseAnchor
>>> ClauseAnchor.objects.filter(is_active=True).count()
14
>>> ClauseAnchor.objects.values('label', 'category')
```

### Step 5: Verify API Endpoints

```bash
# Check if endpoints are registered
curl -X GET http://localhost:8000/api/v1/ai/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# Should show available endpoints (if using DRF browsable API)
```

---

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn clm_backend.wsgi:application --bind 0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.9'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: clm_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      DEBUG: "True"
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/clm_db
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      VOYAGE_API_KEY: ${VOYAGE_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - .:/app

  celery:
    build: .
    command: celery -A clm_backend worker -l info
    environment:
      DEBUG: "False"
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/clm_db
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      VOYAGE_API_KEY: ${VOYAGE_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - .:/app

  flower:
    build: .
    command: celery -A clm_backend flower --port=5555
    ports:
      - "5555:5555"
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - redis

volumes:
  redis_data:
  postgres_data:
```

**Usage:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your-key" > .env
echo "VOYAGE_API_KEY=your-key" >> .env

# Start all services
docker-compose up -d

# Initialize anchors
docker-compose exec web python manage.py initialize_anchors

# View logs
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f flower  # Visit http://localhost:5555
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All API keys in secure secrets management (AWS Secrets Manager, Google Secret Manager)
- [ ] Redis configured for persistence and replication
- [ ] PostgreSQL backups enabled
- [ ] Celery queues monitored (Flower or Sentry)
- [ ] Rate limiting configured
- [ ] Error logging configured (Sentry, CloudWatch)
- [ ] HTTPS enabled
- [ ] CORS configured for production domain
- [ ] DEBUG = False

### Gunicorn Configuration

**gunicorn_config.py:**
```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 60
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

**Run:**
```bash
gunicorn -c gunicorn_config.py clm_backend.wsgi:application
```

### Celery Configuration for Production

**clm_backend/celery.py:**
```python
from celery import Celery
from kombu import Exchange, Queue

app = Celery('clm_backend')

app.conf.update(
    # Task settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Results
    result_expires=3600,  # 1 hour
    
    # Queues
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('priority', Exchange('priority'), routing_key='priority'),
    ),
    task_default_queue='default',
    task_default_priority=5,
)

app.autodiscover_tasks()
```

**Start Celery:**
```bash
celery -A clm_backend worker \
    --loglevel=info \
    --concurrency=4 \
    --prefetch-multiplier=1 \
    --time-limit=3600 \
    --soft-time-limit=3000
```

### Monitoring & Logging

**Error Tracking (Sentry):**
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    environment=os.getenv('ENVIRONMENT', 'production'),
    traces_sample_rate=0.1,
)
```

**Application Monitoring (Datadog):**
```bash
pip install ddtrace
DD_TRACE_ENABLED=true ddtrace-run gunicorn ...
```

---

## Troubleshooting

### Issue: "Failed to connect to Redis"

**Diagnosis:**
```bash
redis-cli ping  # Should return "PONG"
```

**Solutions:**
1. Install Redis: `brew install redis` (macOS)
2. Start Redis: `redis-server`
3. Check configuration: `redis-cli config get port`

### Issue: "Celery task not being processed"

**Diagnosis:**
```bash
# Check Celery worker
celery -A clm_backend inspect active

# Check Celery queue
celery -A clm_backend inspect reserved

# Check Redis queue
redis-cli LLEN celery
```

**Solutions:**
1. Start Celery worker: `celery -A clm_backend worker -l info`
2. Check task configuration in `ai/tasks.py`
3. Verify Redis connection: `redis-cli ping`

### Issue: "Gemini API returns 401 Unauthorized"

**Solutions:**
1. Verify API key: `echo $GEMINI_API_KEY`
2. Check key in Google Cloud Console
3. Regenerate key if expired

### Issue: "No anchor clauses found"

**Solutions:**
```bash
# Re-initialize
python manage.py initialize_anchors --clear

# Verify
python manage.py shell
>>> from ai.models import ClauseAnchor
>>> ClauseAnchor.objects.count()  # Should be 14
```

### Issue: Slow metadata extraction

**Optimization:**
1. Reduce document size (first 8000 chars used)
2. Use faster Gemini model (already using gemini-1.5-flash)
3. Implement caching for repeated documents
4. Scale Celery workers

---

## Performance Tuning

### Database Indexing
```python
# ai/models.py - Already configured:
class Meta:
    indexes = [
        models.Index(fields=['tenant_id', 'status']),
        models.Index(fields=['task_id']),
    ]
```

### Query Optimization
```python
# Use select_related for foreign keys
DocumentChunk.objects.select_related('document').filter(...)

# Use only() to limit fields
ClauseAnchor.objects.only('id', 'embedding', 'label').filter(...)
```

### Caching
```python
from django.core.cache import cache

# Cache embeddings
embedding = cache.get(f"embedding:{text_hash}")
if not embedding:
    embedding = embeddings_service.embed_text(text)
    cache.set(f"embedding:{text_hash}", embedding, timeout=86400)  # 24 hours
```

---

## Testing

### Unit Tests
```python
# ai/tests.py
from django.test import TestCase
from ai.models import ClauseAnchor

class ClauseAnchorTests(TestCase):
    def test_anchor_creation(self):
        anchor = ClauseAnchor.objects.create(
            label="Confidentiality",
            category="Legal",
            description="Test",
            example_text="Test text",
            embedding=[0.1, 0.2, ...],
            is_active=True
        )
        self.assertEqual(anchor.label, "Confidentiality")
```

### Integration Tests
```bash
# Run test suite
python manage.py test ai

# Coverage
pip install coverage
coverage run --source='ai' manage.py test ai
coverage report
```

### Load Testing
```bash
pip install locust

# locustfile.py
from locust import HttpUser, task

class AIUser(HttpUser):
    @task
    def classify_clause(self):
        self.client.post("/api/v1/ai/classify/", json={
            "text": "Confidential information..."
        })

# Run: locust -f locustfile.py --host=http://localhost:8000
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check Celery queue depth
- Review error logs (Sentry)
- Verify API key quotas

**Monthly:**
- Optimize database indexes
- Archive old draft generation tasks
- Review and update anchor clauses if needed

**Quarterly:**
- Upgrade dependencies: `pip list --outdated`
- Review and refactor code
- Update documentation

### Updating Anchor Clauses

```python
# Add new anchor
from ai.models import ClauseAnchor

ClauseAnchor.objects.create(
    label="New Clause Type",
    category="Category",
    description="Description",
    example_text="Example text...",
    embedding=[...],  # Generated by VoyageEmbeddingsService
    is_active=True
)

# Or re-initialize all
python manage.py initialize_anchors --clear
```

---

## Support

### Resources
- [AI_ENDPOINTS_COMPLETE.md](./AI_ENDPOINTS_COMPLETE.md) - Detailed API documentation
- [Gemini API Docs](https://ai.google.dev/)
- [Voyage AI Docs](https://docs.voyageai.com/)
- [Celery Docs](https://docs.celeryproject.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)

### Contact
For issues or questions, open an issue on the repository or contact the development team.
