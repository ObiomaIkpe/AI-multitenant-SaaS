# app/models/tenant.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from app.database import Base # Assuming your Base is defined here

def generate_safe_schema_name():
    return "s_" + str(uuid.uuid4()).hex 

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"} 

    id = Column(Integer, primary_key=True, index=True)
    
    # User-facing name (e.g., "Acme Corp")
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Used for domain-based routing (e.g., "acme.mysaas.com")
    domain = Column(String, unique=True, index=True, nullable=True) 
    
    # The actual PostgreSQL schema name for data isolation
    # Uses the helper function to generate a unique, non-guessable name
    schema_name = Column(String, unique=True, index=True, 
                          default=generate_safe_schema_name, nullable=False)
                          
    # Billing/Suspension control: If False, access should be blocked
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamp for tracking when the tenant was created
    created_at = Column(DateTime, default=datetime.utcnow, 
                         server_default=text("CURRENT_TIMESTAMP"), nullable=False)