from fastapi import APIRouter

from app.api.endpoints import users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
# Add other routers here later (e.g., projects, forests, calculations)
# api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

print("API router configured with user endpoints.")

