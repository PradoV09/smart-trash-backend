from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from enum import Enum
import re

class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    driver = "driver"

class UserCreate(BaseModel):
    id: Optional[int] = Field(None, description="The unique identifier of the user")
    role: UserRole = Field(..., description="The role of the user")
    name: str = Field(min_length=2, max_length=50, description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    password: str = Field(min_length=6, description="The password of the user")

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid email address')
        return value.lower()

class ResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")
    role: str = Field(..., description="The role of the user")