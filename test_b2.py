import os
from dotenv import load_dotenv
load_dotenv()

print("B2_KEY_ID:", os.getenv('B2_KEY_ID'))
print("B2_APPLICATION_KEY:", os.getenv('B2_APPLICATION_KEY')[:20] + "...")

from core.storage import upload_to_b2

# Test upload
test_data = b"This is a test file"
result = upload_to_b2(test_data, "test.txt")
print("Upload result:", result)