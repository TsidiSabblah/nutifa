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