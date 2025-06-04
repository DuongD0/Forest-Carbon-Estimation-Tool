from fastapi import APIRouter

from app.api.endpoints import users, projects, forests

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(forests.router, prefix="/forests", tags=["forests"])
# Add other routers here later (e.g., calculations)

print("API router configured with user, project, and forest endpoints.")

