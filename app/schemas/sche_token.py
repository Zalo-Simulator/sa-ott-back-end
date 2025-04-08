from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    user_id: Optional[int] = None

class LoginResponse(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str]
    access_token: str 
    token_type: str 

class ChangePassword(BaseModel):
    current_password: str
    new_password: str 

class ResetPassword(BaseModel):
    phone: str 
    password: str 