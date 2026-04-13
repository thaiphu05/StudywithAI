from fastapi import APIRouter, Depends, HTTPException
from src.schemas.auth import LoginRequest, LoginResponse
from src.api.dependencies import get_auth_service
from src.services.auth_service import AuthService

router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    try:
        auth_token, account_id = auth_service.login(
            username=payload.username,
            password=payload.password
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return LoginResponse(auth_token=auth_token, account_id=account_id)

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
