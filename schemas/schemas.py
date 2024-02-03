from typing import Any

from pydantic import BaseModel, SecretStr


class LoginInfo(BaseModel):
    email: str
    password: SecretStr

    def to_dict(self) -> dict:
        return {"email": self.email, "password": self.password.get_secret_value()}


class SessionUserData(BaseModel):
    id: int
    email: str
    cookies: Any  # real type is RequestsCookieJar


class BucketInfo(BaseModel):
    access_key_id: str
    secret_key: str
    bucket_name: str


class DNRFileNames(BaseModel):
    request: str
    raw_screen_usage: str
    solution_values: str
    mps: str
