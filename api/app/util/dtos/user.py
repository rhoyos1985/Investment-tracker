from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional

class UserDTO(BaseModel):
    id: Optional[str] = None
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="First name of the user (required, 1-50 characters)"
    )
    last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Last name of the user (required, 1-50 characters)"
    )
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="username unique (required, 3-50 characters without spaces)"
    )
    email: EmailStr = Field(
        ...,
        description="Email address of the user (required, valid email format)"
    )
    password: str = Field(
        ..., 
        min_length=6,
        description="Password of the user (required, at least 6 characters with numbers or special characters)"
    )
    is_active: Optional[bool] = Field(default=True)
    is_admin: Optional[bool] = Field(default=False)

    @field_validator('first_name', 'last_name', 'username', 'email', 'password', mode='before')
    def check_required_fields(cls, v, field):
        if isinstance(v, str) and not v.strip():
            print(f'Validation error: {field.name} is required and cannot be empty')
            raise ValueError(f'{field.name} is required and cannot be empty')
        return v
    
    @field_validator('username')
    def validate_username(cls, v):
        if ' ' in v:
            raise ValueError('The username cannot contain spaces')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        if v.isalpha():
            raise ValueError('La contraseña debe contener al menos un número o carácter especial')
        return v
