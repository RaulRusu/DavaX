from fastapi import APIRouter

router = APIRouter(prefix="/test")

@router.get("/{msg}")
def read_user(msg: str):
    return f"hello {msg}"