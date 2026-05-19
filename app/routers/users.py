from fastapi import APIRouter, Depends
from app.schemas import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    return User(id=user_id, role="user")
