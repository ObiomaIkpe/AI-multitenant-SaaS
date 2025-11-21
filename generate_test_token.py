from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

# 1. Define your test tenant
TEST_TENANT_ID = "tenant_alpha_123"

# 2. Create the payload with the tenant_id and expiration
payload = {
    "tenant_id": TEST_TENANT_ID,
    "exp": datetime.now(timezone.utc) + timedelta(hours=1) # Valid for 1 hour
}

# 3. Sign the token using your project's SECRET_KEY
token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

print("\n--- YOUR TEST JWT TOKEN ---")
print(token)
print("---------------------------\n")