from fastapi import FastAPI

app = FastAPI(
    title="Forest Carbon Credit Estimation Tool API",
    description="API for managing forest data and calculating carbon credits.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Forest Carbon Credit Estimation Tool API"}

# Placeholder for future routers
# from .routers import users, projects, forests, calculations
# app.include_router(users.router)
# app.include_router(projects.router)
# app.include_router(forests.router)
# app.include_router(calculations.router)

print("FastAPI application initialized.")

