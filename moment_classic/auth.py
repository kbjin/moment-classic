# Basic Auth
import os
import secrets

from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBasicCredentials, HTTPBasic

security = HTTPBasic()

# 기본 인증 정보
BASIC_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
BASIC_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
API_KEY = os.getenv("API_KEY")


def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, BASIC_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, BASIC_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# API Key Auth
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


def auth_or_api_key(
    credentials: HTTPBasicCredentials = Depends(security),
    x_api_key: str = Header(None),
):
    # API 키가 맞으면 통과
    if x_api_key and secrets.compare_digest(x_api_key, API_KEY):
        return True
    # Basic Auth가 맞으면 통과
    if (
        credentials
        and secrets.compare_digest(credentials.username, BASIC_USERNAME)
        and secrets.compare_digest(credentials.password, BASIC_PASSWORD)
    ):
        return True
    # 둘 다 실패하면 차단
    raise HTTPException(
        status_code=401, detail="Not authorized (API key or Basic Auth required"
    )
