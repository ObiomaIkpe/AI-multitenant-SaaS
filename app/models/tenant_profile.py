from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Base is typically defined once for your application
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Defines the relationship to Profile
    # uselist=False tells SQLAlchemy this is a one-to-one relationship
    profile = relationship(
        "Profile", 
        back_populates="user", 
        uselist=False
    )
    
class Profile(Base):
    __tablename__ = "tenant_profiles"
    id = Column(Integer, primary_key=True)
    bio = Column(String)
    
    # Foreign Key links Profile back to User
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Defines the reverse relationship back to User
    # Note: The 'unique=True' on the ForeignKey is CRITICAL 
    # for database-level enforcement of the one-to-one constraint.
    user = relationship("User", back_populates="profile")