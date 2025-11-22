from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse
from app.crud.user import create_user_with_tenant, authenticate_user, get_user_by_email
from app.core.config import settings
from app.core.security import get_current_tenant_id

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user and create their tenant.
    Returns JWT token for immediate login.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user and tenant
    user, tenant = await create_user_with_tenant(
        db=db,
        email=user_data.email,
        password=user_data.password,
        tenant_name=user_data.tenant_name
    )
    
    # Generate token
    access_token = create_access_token(
        data={settings.TENANT_ID_FIELD: tenant.id, "sub": user.email}
    )
    
    return Token(access_token=access_token, tenant_id=tenant.id)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user's tenant
    if not user.tenant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User has no associated tenant"
        )
    
    # Generate token
    access_token = create_access_token(
        data={settings.TENANT_ID_FIELD: user.tenant.id, "sub": user.email}
    )
    
    return Token(access_token=access_token, tenant_id=user.tenant.id)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's information.
    Requires valid JWT token.
    """
    from app.models.document import Tenant
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    
    result = await db.execute(
        select(Tenant)
        .options(selectinload(Tenant.owner))
         .where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return UserResponse(
        id=tenant.owner.id,
        email=tenant.owner.email,
        tenant_id=tenant.id,
        tenant_name=tenant.name
    )