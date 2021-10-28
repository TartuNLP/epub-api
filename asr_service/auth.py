import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

class Auth:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_username(self, credentials: HTTPBasicCredentials = Depends(security)):
        correct_username = secrets.compare_digest(credentials.username, self.username)
        correct_password = secrets.compare_digest(credentials.password, self.password)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username