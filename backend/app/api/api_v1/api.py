from fastapi import APIRouter
from app.api.endpoints import users, projects, ecosystems, p2p, calculate, geospatial, export

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(ecosystems.router, prefix="/ecosystems", tags=["ecosystems"])
api_router.include_router(p2p.router, prefix="/p2p", tags=["p2p"])
api_router.include_router(calculate.router, prefix="/calculate", tags=["calculate"])
api_router.include_router(geospatial.router, prefix="/geospatial", tags=["geospatial"])
api_router.include_router(export.router, prefix="/export", tags=["export"]) 