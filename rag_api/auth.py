from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify the authorization token"""
    token = credentials.credentials
    valid_token = os.getenv("API_TOKEN")
    
    if not valid_token:
        raise HTTPException(
            status_code=500,
            detail="API_TOKEN not configured"
        )
    
    if token != valid_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    return token