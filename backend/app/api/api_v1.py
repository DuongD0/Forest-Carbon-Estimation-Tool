from fastapi import APIRouter

from app.api.endpoints import users, projects, forests, imagery, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(forests.router, prefix="/forests", tags=["forests"])
api_router.include_router(imagery.router, prefix="/imagery", tags=["imagery"])
# Add other routers here later (e.g., calculations)

print("API router configured with user, project, forest, and imagery endpoints.")

