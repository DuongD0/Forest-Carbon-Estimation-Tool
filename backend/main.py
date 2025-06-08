from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.api_v1 import api_router
from app.db.session import engine # Import engine if needed for initial setup/check
# from app.db.base import Base # Import Base if creating tables directly (not recommended with Alembic)

# If using Alembic, table creation is handled by migrations.
# Otherwise, uncomment the following line to create tables on startup (for simple cases):
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Forest Carbon Credit Estimation Tool API",
    description="API for managing forest data and calculating carbon credits.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json", # Standard OpenAPI path
    docs_url=None, # Disable default docs
    redoc_url=None # Disable redoc
)

# Serve the Stoplight Elements documentation
@app.get("/apidocs", include_in_schema=False)
async def get_elements_docs() -> HTMLResponse:
    with open("app/static/elements.html") as f:
        return HTMLResponse(f.read())

# Include the API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Forest Carbon Credit Estimation Tool API. Docs at /apidocs."}

print("FastAPI application initialized with API v1 router.")

