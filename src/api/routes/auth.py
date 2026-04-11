from fastapi import APIRouter, Depends, HTTPException
from src.api.auth.security import LoginRequest, LoginResponse
from src.services.auth_service import AuthService

auth_service = AuthService()
router = APIRouter()

@router.post("/login")
def login(payload: LoginRequest) -> LoginResponse:
    try:
        auth_token, account_id = auth_service.login(
            username=payload.username,
            password=payload.password
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return LoginResponse(auth_token=auth_token, account_id=account_id)

@router.post("/logout")
def logout():
    # Placeholder for actual logout logic
    return {"message": "Logged out successfully"}
