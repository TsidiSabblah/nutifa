import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from dotenv import load_dotenv

load_dotenv()

B2_KEY_ID = os.getenv('B2_KEY_ID')
B2_APPLICATION_KEY = os.getenv('B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.getenv('B2_BUCKET_NAME', 'nutifa-music')

def get_b2_api():
    """Initialize B2 API connection"""
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", B2_KEY_ID, B2_APPLICATION_KEY)
        print("✅ B2 API connected successfully")
        return b2_api
    except Exception as e:
        print(f"❌ B2 API connection failed: {e}")
        return None

def get_b2_bucket():
    """Get or create bucket"""
    b2_api = get_b2_api()
    if not b2_api:
        return None
    
    try:
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        print(f"✅ Bucket '{B2_BUCKET_NAME}' found")
        return bucket
    except Exception as e:
        try:
            print(f"Bucket not found, creating: {e}")
            bucket = b2_api.create_bucket(B2_BUCKET_NAME, 'allPrivate')
            print(f"✅ Bucket '{B2_BUCKET_NAME}' created")
            return bucket
        except Exception as create_error:
            print(f"❌ Failed to create bucket: {create_error}")
            return None

def upload_to_b2(file_data, filename):
    """Upload file to Backblaze B2"""
    try:
        bucket = get_b2_bucket()
        if not bucket:
            print("❌ No bucket available")
            return None
        
        uploaded_file = bucket.upload_bytes(
            file_data,
            filename,
            content_type='audio/mpeg'
        )
        print(f"✅ Uploaded to B2: {filename}")
        return {'file_name': uploaded_file.file_name}
    except Exception as e:
        print(f"❌ Upload to B2 failed: {e}")
        return None

def get_download_url(filename, expires_in=3600):
    """Get download URL for a file (public or authorized)"""
    try:
        bucket = get_b2_bucket()
        if not bucket:
            print("❌ No bucket available")
            return None
        
        # Get download URL (works for private buckets)
        download_url = bucket.get_download_url(filename)
        return download_url
    except Exception as e:
        print(f"❌ Get download URL failed: {e}")
        return None

def delete_from_b2(filename):
    """Delete file from B2"""
    try:
        bucket = get_b2_bucket()
        if not bucket:
            return False
        
        # Get file info
        file_version = bucket.get_file_info_by_name(filename)
        if file_version:
            bucket.delete_file_version(file_version.id_, file_version.file_name)
            print(f"✅ Deleted from B2: {filename}")
        return True
    except Exception as e:
        print(f"❌ Delete from B2 failed: {e}")
        return False

def file_exists_in_b2(filename):
    """Check if file exists in B2"""
    try:
        bucket = get_b2_bucket()
        if not bucket:
            return False
        
        file_info = bucket.get_file_info_by_name(filename)
        return file_info is not None
    except:
        return False