"""
SignNow E-Signature API URLs
"""

from django.urls import path
from . import signnow_views

urlpatterns = [
    # Upload contract to SignNow
    path('contracts/upload/', signnow_views.upload_contract, name='upload_contract'),
    
    # Send for signature
    path('esign/send/', signnow_views.send_for_signature, name='send_for_signature'),
    
    # Generate signing URL
    path('esign/signing-url/<str:contract_id>/', signnow_views.get_signing_url, name='get_signing_url'),
    
    # Check status (polling)
    path('esign/status/<str:contract_id>/', signnow_views.check_status, name='check_status'),
    
    # Download executed document
    path('esign/executed/<str:contract_id>/', signnow_views.get_executed_document, name='get_executed_document'),
]
