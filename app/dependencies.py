from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Tenant

# 2a. Basic DB Session Dependency (for fetching the Tenant record)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2b. Tenant ID Extraction Dependency
def get_tenant_id(
    x_tenant_id: str = Header(..., description="Unique ID of the tenant")
) -> int:
    """Extracts the Tenant ID from the request header."""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header required.")
    # In a real app, you might validate this is a JWT token and extract the ID
    try:
        # Assuming X-Tenant-ID header contains the integer ID for simplicity
        return int(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Tenant ID format.")
    
# Continuing in app/dependencies.py

def get_tenant_db(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db)
) -> Session:
    """
    Dependency that establishes a DB session and sets the search_path
    to the correct tenant schema.
    """
    
    # 1. Look up the tenant record using the ID from the header
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or inactive.")
    
    schema_name = tenant.schema_name
    
    # 2. Open a new session to ensure isolation
    tenant_db = SessionLocal()
    
    try:
        # 3. CRITICAL: Execute SET search_path to direct all queries
        # The 'public' schema is included as a fallback for shared tables (like 'tenants')
        tenant_db.execute(
            f"SET search_path TO {schema_name}, public"
        )
        # 4. Yield the session to the route handler
        yield tenant_db
        
    except Exception:
        tenant_db.rollback()
        raise
        
    finally:
        # 5. Always close the session
        tenant_db.close()