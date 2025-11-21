from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    tenant = relationship("Tenant", back_populates="owner", uselist=False)
    
    def __repr__(self):
        return f"<User {self.email}>"


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Quotas for 200 users/month - keep it generous
    max_documents = Column(Integer, default=100)
    max_queries_per_day = Column(Integer, default=100)
    
    # Relationships
    owner = relationship("User", back_populates="tenant")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant {self.name}>"


class DocumentStatus(enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String, nullable=False)
    
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PROCESSING, nullable=False)
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    processed_at = Column(DateTime, nullable=True)
    
    # Relationship
    tenant = relationship("Tenant", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.filename} - {self.status.value}>"