import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv

load_dotenv()

# Backblaze B2 Configuration
B2_KEY_ID = os.getenv('B2_KEY_ID')
B2_APPLICATION_KEY = os.getenv('B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.getenv('B2_BUCKET_NAME', 'nutifa-music')

def get_b2_api():
    """Initialize B2 API connection"""
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", B2_KEY_ID, B2_APPLICATION_KEY)
    return b2_api

def get_b2_bucket():
    """Get or create bucket"""
    b2_api = get_b2_api()
    try:
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
    except:
        # Create bucket if it doesn't exist
        bucket = b2_api.create_bucket(B2_BUCKET_NAME, 'allPrivate')
    return bucket

def upload_to_b2(file_data, filename, content_type='audio/mpeg'):
    """Upload file to Backblaze B2"""
    try:
        bucket = get_b2_bucket()
        # Upload file
        uploaded_file = bucket.upload_bytes(
            file_data,
            filename,
            content_type=content_type
        )
        # Return file ID and download URL
        return {
            'file_id': uploaded_file.id_,
            'file_name': uploaded_file.file_name,
            'url': bucket.get_download_url(filename)
        }
    except Exception as e:
        print(f"Upload to B2 failed: {e}")
        return None

def get_download_url(filename, expires_in=3600):
    """Get authorized download URL (private file)"""
    try:
        bucket = get_b2_bucket()
        # Generate authorization token for download
        download_url = bucket.get_download_url(filename)
        return download_url
    except Exception as e:
        print(f"Get download URL failed: {e}")
        return None

def delete_from_b2(filename):
    """Delete file from B2"""
    try:
        bucket = get_b2_bucket()
        file_version = bucket.get_file_info_by_name(filename)
        if file_version:
            bucket.delete_file_version(file_version.id_, file_version.file_name)
        return True
    except Exception as e:
        print(f"Delete from B2 failed: {e}")
        return False

def file_exists_in_b2(filename):
    """Check if file exists in B2"""
    try:
        bucket = get_b2_bucket()
        file_info = bucket.get_file_info_by_name(filename)
        return file_info is not None
    except:
        return False