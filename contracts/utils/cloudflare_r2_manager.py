"""
Cloudflare R2 Storage Manager
Handles all contract uploads, downloads, and management
"""

import boto3
import os
import json
from datetime import datetime, timedelta
from django.conf import settings
from botocore.exceptions import ClientError


class CloudflareR2Manager:
    """Manages contract storage in Cloudflare R2"""
    
    def __init__(self):
        """Initialize R2 client"""
        self.bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'contracts-production')
        self.region = os.getenv('AWS_S3_REGION_NAME', 'auto')
        self.endpoint_url = os.getenv('AWS_S3_ENDPOINT_URL')
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.custom_domain = os.getenv('AWS_S3_CUSTOM_DOMAIN', 'r2.cloudflare.com')
        
        # Initialize S3 client for R2
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    def upload_contract(self, contract_id, pdf_content, filename, metadata=None):
        """
        Upload contract PDF to Cloudflare R2
        
        Args:
            contract_id: UUID of contract
            pdf_content: Binary PDF content
            filename: Original filename
            metadata: Additional metadata
        
        Returns:
            dict: Upload result with URL
        """
        try:
            # Create object key
            timestamp = datetime.now().strftime('%Y/%m/%d')
            object_key = f'contracts/{timestamp}/{contract_id}/{filename}'
            
            # Prepare metadata
            tags = {
                'contract_id': contract_id,
                'upload_date': datetime.now().isoformat(),
                'filename': filename
            }
            if metadata:
                tags.update(metadata)
            
            # Upload to R2
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=pdf_content,
                ContentType='application/pdf',
                Metadata=tags,
                CacheControl='max-age=31536000'  # 1 year cache
            )
            
            # Generate public URL
            public_url = f'https://{self.custom_domain}/{object_key}'
            
            return {
                'success': True,
                'object_key': object_key,
                'public_url': public_url,
                'size': len(pdf_content),
                'uploaded_at': datetime.now().isoformat()
            }
        
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': e.response['Error']['Code']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_contract(self, object_key):
        """
        Download contract from Cloudflare R2
        
        Args:
            object_key: S3 object key
        
        Returns:
            Binary PDF content or None
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return response['Body'].read()
        except ClientError as e:
            return None
    
    def delete_contract(self, object_key):
        """Delete contract from R2"""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return {'success': True, 'message': 'Contract deleted'}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def list_contracts(self, prefix='contracts/'):
        """List all contracts in R2"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'url': f'https://{self.custom_domain}/{obj["Key"]}'
                    })
            
            return {'success': True, 'files': files}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def get_signed_url(self, object_key, expiration=3600):
        """
        Generate signed URL for temporary access
        
        Args:
            object_key: S3 object key
            expiration: URL expiration in seconds (default: 1 hour)
        
        Returns:
            Signed URL string
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            return None
    
    def get_contract_metadata(self, object_key):
        """Get metadata for contract"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return {
                'success': True,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'].isoformat(),
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def copy_contract(self, source_key, destination_key):
        """Copy contract from source to destination"""
        try:
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=destination_key
            )
            return {'success': True, 'destination_key': destination_key}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def archive_contract(self, object_key):
        """Move contract to archive folder"""
        archive_key = object_key.replace('contracts/', 'archive/')
        return self.copy_contract(object_key, archive_key)
    
    def get_bucket_stats(self):
        """Get bucket statistics"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name
            )
            
            total_size = 0
            total_objects = 0
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_size += obj['Size']
                    total_objects += 1
            
            return {
                'success': True,
                'bucket_name': self.bucket_name,
                'total_objects': total_objects,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except ClientError as e:
            return {'success': False, 'error': str(e)}


# Singleton instance
_r2_manager = None

def get_r2_manager():
    """Get or create R2 manager instance"""
    global _r2_manager
    if _r2_manager is None:
        _r2_manager = CloudflareR2Manager()
    return _r2_manager
