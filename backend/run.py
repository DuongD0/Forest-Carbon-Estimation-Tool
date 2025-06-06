import uvicorn
import typer
import os
from alembic.config import Config
from alembic import command

from main import app

cli = typer.Typer()

@cli.command()
def run_server():
    """
    Run the FastAPI development server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

@cli.command()
def create_db():
    """
    Applies all Alembic migrations to the database.
    """
    print("Applying database migrations...")
    alembic_cfg = Config("backend/alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations applied successfully.")

@cli.command()
def another_command():
    """
    Placeholder for another command.
    """
    print("This is another command.")

if __name__ == "__main__":
    cli() 