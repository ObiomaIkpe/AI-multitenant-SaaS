from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    tenant_name: str = Field(..., min_length=1, max_length=100, description="Your organization name")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str

class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
    tenant_name: str
    
    class Config:
        from_attributes = True