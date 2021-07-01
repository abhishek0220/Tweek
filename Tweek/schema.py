import os
from pydantic import BaseModel, validator

AUTH_KEY = os.environ['AUTH_KEY']


class WebSocketMessage(BaseModel):
    auth_code: str
    action: str
    description: str = ''

    @validator('auth_code', pre=True)
    def pw_creation(cls, v: str):
        if v != AUTH_KEY:
            raise ValueError("Invalid AUTH_KEY")
        return ''
