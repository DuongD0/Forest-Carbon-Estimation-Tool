from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
import json

from app.api.api_v1.api import api_router

app = FastAPI(
    title="Forest Carbon Estimation Tool API",
    openapi_url="/api/v1/openapi.json",
    docs_url=None, 
    redoc_url=None,
)

# Print startup message
print("FastAPI application initialized with API v1 router.")

# Configure CORS with Starlette directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Forest Carbon Credit Estimation Tool API. Docs at /apidocs"}

@app.get("/apidocs", include_in_schema=False)
async def get_api_docs() -> HTMLResponse:
    try:
        with open("app/static/apidocs.html", "r") as f:
            html_content = f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>API Documentation not found</h1>", status_code=500)

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    
    html_with_schema = html_content.replace(
        "const apiDescriptionDocument = {};",
        f"const apiDescriptionDocument = {json.dumps(openapi_schema)};"
    )

    return HTMLResponse(content=html_with_schema) 