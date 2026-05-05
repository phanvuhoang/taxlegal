from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from backend.database import get_db
from backend.models import User
from backend.auth import verify_password, create_access_token, hash_password, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản bị vô hiệu hoá")
    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
    }


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.post("/change-password")
async def change_password(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")
    if not verify_password(old_pw, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")
    if len(new_pw) < 8:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải ≥8 ký tự")
    current_user.password_hash = hash_password(new_pw)
    await db.commit()
    return {"message": "Đổi mật khẩu thành công"}
