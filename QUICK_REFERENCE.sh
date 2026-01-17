#!/bin/bash
################################################################################
# QUICK REFERENCE - Search Endpoints Usage Guide
################################################################################

# ============================================================================
# 1. START SERVER
# ============================================================================
cd /Users/vishaljha/CLM_Backend
python manage.py runserver 11000

# ============================================================================
# 2. GET JWT TOKEN (REQUIRED FOR ALL REQUESTS)
# ============================================================================
curl -X POST http://localhost:11000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test_search@test.com", "password": "Test@1234"}'

# Save token:
JWT="<paste token here>"

# ============================================================================
# 3. KEYWORD SEARCH (RETURNS REAL DATA - 5 RESULTS)
# ============================================================================
curl -X GET "http://localhost:11000/api/search/keyword/?q=confidentiality&limit=10" \
  -H "Authorization: Bearer $JWT"

# Returns: 5 real Confidentiality Agreement documents

# ============================================================================
# 4. SEMANTIC SEARCH (VECTOR SIMILARITY)
# ============================================================================
curl -X GET "http://localhost:11000/api/search/semantic/?q=confidentiality&threshold=0.5&top_k=10" \
  -H "Authorization: Bearer $JWT"

# Parameters:
#   q=<query>          - Search term
#   threshold=<0-1>    - Similarity threshold (default 0.5)
#   top_k=<number>     - Max results to return (default 10)

# ============================================================================
# 5. ADVANCED SEARCH (WITH FILTERS)
# ============================================================================
curl -X POST http://localhost:11000/api/search/advanced/ \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "confidential",
    "filters": {"document_type": "contract"},
    "top_k": 10
  }'

# ============================================================================
# 6. HEALTH CHECK
# ============================================================================
curl http://localhost:11000/api/health/

# Returns: {"status": "healthy", "service": "CLM Backend"}

# ============================================================================
# RUN TEST SUITE
# ============================================================================

# Quick test
bash FINAL_TEST_SUITE.sh

# Full test
bash test_search_endpoints.sh

# ============================================================================
# DATABASE QUERIES
# ============================================================================

# Check chunks for user
python manage.py shell <<'EOF'
from repository.models import DocumentChunk
from django.contrib.auth import get_user_model

user = get_user_model().objects.get(email='test_search@test.com')
chunks = DocumentChunk.objects.filter(document__tenant_id=user.tenant_id)
print(f"Chunks: {chunks.count()}")
EOF

# ============================================================================
# SAMPLE RESPONSES
# ============================================================================

# Keyword Search Response (5 RESULTS):
# {
#     "success": true,
#     "query": "confidentiality",
#     "search_type": "keyword",
#     "count": 5,
#     "results": [
#         {
#             "chunk_id": "e16a60a5-9eca-4e31-b7ef-c78d89e4b43a",
#             "text": "CONFIDENTIALITY AGREEMENT ...",
#             "document_id": "30b4bd41-f46b-4b93-9922-1b2aa1a2d01f",
#             "filename": "sample_agreement.txt",
#             "document_type": "contract"
#         },
#         ... 4 more ...
#     ]
# }

# ============================================================================
# KEY ENDPOINTS SUMMARY
# ============================================================================
# GET  /api/health/                    - Health check
# POST /api/auth/login/                - Get JWT token
# GET  /api/search/keyword/            - Keyword search (WORKING ✓)
# GET  /api/search/semantic/           - Vector similarity search
# POST /api/search/advanced/           - Advanced search with filters

# ============================================================================
# IMPORTANT CREDENTIALS
# ============================================================================
# Email: test_search@test.com
# Password: Test@1234
# Tenant: test_tenant_f418c82e (45434a45-4914-4b88-ba5d-e1b5d2c4cf5b)
# Server Port: 11000

# ============================================================================
# VERIFICATION POINTS
# ============================================================================
# ✓ Keyword search returns 5 real results
# ✓ JWT tokens are 277 characters
# ✓ All responses are valid JSON with HTTP 200
# ✓ Rate limiting: 20 seconds between calls (3/min)
# ✓ Database: 28 chunks with embeddings
# ✓ Test user can access documents in tenant

# ============================================================================
# DEBUGGING COMMANDS
# ============================================================================

# Check test user
python manage.py shell -c "from django.contrib.auth import get_user_model; u=get_user_model().objects.get(email='test_search@test.com'); print(f'Tenant: {u.tenant_id}')"

# Check chunks
python manage.py shell -c "from repository.models import DocumentChunk; print(f'Total: {DocumentChunk.objects.count()}')"

# Check embeddings
python manage.py shell -c "from repository.models import DocumentChunk; emb=DocumentChunk.objects.exclude(embedding__isnull=True).count(); print(f'With embeddings: {emb}')"

# View server logs
# Check terminal where server is running for debug output

################################################################################
