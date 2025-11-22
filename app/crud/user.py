from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import User, Tenant
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant))  # ← Add this line
        .where(User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user_with_tenant(db: AsyncSession, email: str, password: str, tenant_name: str) -> tuple[User, Tenant]:
    """
    Creates a new user and their tenant in a single transaction.
    Returns (user, tenant) tuple.
    """
    # Create user
    hashed_password = hash_password(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.flush()  # Get user.id without committing
    
    # Create tenant for the user
    tenant = Tenant(name=tenant_name, owner_id=user.id)
    db.add(tenant)
    
    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)
    
    return user, tenant


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Validates user credentials.
    Returns User if valid, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user