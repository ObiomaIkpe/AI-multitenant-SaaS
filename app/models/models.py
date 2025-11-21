class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"} # Explicitly put in public schema

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    # This is the key that tells you which schema to use
    schema_name = Column(String, unique=True, index=True) 
    domain = Column(String, unique=True)