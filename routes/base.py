from fastapi import APIRouter

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/welcome")
def welcome():
    return {"message": "Welcome to Social Media App!"}
