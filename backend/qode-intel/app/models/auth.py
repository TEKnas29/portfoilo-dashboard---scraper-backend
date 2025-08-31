from pydantic import BaseModel


class LoginStatus(BaseModel):
    is_logged_in: bool
    message: str


class LoginCredentials(BaseModel):
    username: str
    password: str
