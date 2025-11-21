from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # <--- Added HTTPAuthorizationCredentials and HTTPBearer
from jose import jwt, JWTError
from app.core.config import settings

# We use HTTPBearer for standard "Authorization: Bearer <token>" header handling.
# This scheme expects the client to send: Authorization: Bearer <token>
security = HTTPBearer()

def get_current_tenant_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Decodes the JWT token, validates the signature, and extracts the tenant_id.
    This function is used as a dependency in secure routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials # Extract the actual token string

    try:
        # 1. Decode the token using the SECRET_KEY from settings
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 2. Extract the tenant_id
        tenant_id: str = payload.get(settings.TENANT_ID_FIELD)
        
        if tenant_id is None:
            print("❌ Token missing tenant_id")
            raise credentials_exception
            
        return tenant_id

    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception