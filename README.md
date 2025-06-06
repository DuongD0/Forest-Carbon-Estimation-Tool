# Forest Carbon Credit Estimation Tool

This project is a comprehensive web-based tool for estimating forest carbon credits in Vietnam. It leverages satellite/drone imagery analysis, geospatial data processing, and established scientific methodologies to provide accurate and reliable carbon credit calculations. The tool is designed for use by environmental agencies, project developers, and researchers.

## Key Features

*   **User & Project Management**: Secure authentication and role-based access control for managing users and carbon projects.
*   **Geospatial Data Handling**: Supports uploading and managing project boundaries, forest areas (polygons), and sample plots using GeoJSON.
*   **Imagery Processing**: Upload and process satellite or drone imagery. The backend can classify forest types based on HSV color signatures tailored for Vietnamese ecosystems.
*   **Carbon Calculation Pipeline**: A full pipeline that:
    *   Calculates biomass at the plot and forest level using allometric equations.
    *   Derives carbon stock from biomass.
    *   Establishes a baseline scenario.
    *   Quantifies net creditable carbon credits after accounting for leakage and risk buffers.
*   **RESTful API**: A robust backend API built with FastAPI provides access to all functionalities.
*   **Web-based Frontend**: An intuitive user interface built with React and TypeScript for easy interaction with the system.
*   **Database**: PostgreSQL with PostGIS for powerful and efficient spatial data storage and queries.
*   **Containerized Deployment**: Docker and Docker Compose for easy setup and deployment.

## Project Structure

The project is organized into a `backend` (FastAPI) and a `frontend` (React) application.

```
/
├── backend/           # FastAPI backend application
│   ├── alembic/       # Database migrations
│   ├── app/           # Core application source code
│   │   ├── api/       # API endpoints (routers)
│   │   ├── core/      # Configuration, security
│   │   ├── crud/      # CRUD database operations
│   │   ├── db/        # Database session and initialization
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── processing/# Business logic (carbon, image, geo)
│   │   └── schemas/   # Pydantic data validation schemas
│   ├── main.py        # App entry point
│   └── ...
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   └── ...
├── tests/             # Backend test suite
└── docker-compose.yml # Docker Compose configuration
```

## Technology Stack

*   **Backend**: Python, FastAPI, SQLAlchemy, Alembic, GeoAlchemy2, Pydantic, PostgreSQL + PostGIS
*   **Frontend**: TypeScript, React, Material-UI (MUI)
*   **Geospatial**: Rasterio, GeoPandas, Shapely, PyPROJ
*   **Deployment**: Docker, Docker Compose

## Local Development Setup

### Prerequisites

*   Docker and Docker Compose installed.
*   `conda` for managing Python environment (recommended).

### Backend Setup

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```

2.  **Set up the environment.** It is recommended to use the `Forest` conda environment as specified in the project's memory.
    ```bash
    # (If you have conda)
    conda env create -f environment.yml # Or create from requirements.txt
    conda activate Forest
    ```

3.  **Create a `.env` file** from the example and fill in your configuration:
    ```bash
    cp .env.example .env
    ```

4.  **Launch services using Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    This will start the FastAPI backend server and the PostgreSQL database.

5.  **Apply database migrations:**
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

6.  **(Optional) Load initial data:**
    This will create a default admin user and some reference data (e.g., allometric equations for Vietnam).
    ```bash
    docker-compose exec backend python -m app.db.initial_data
    ```

### Frontend Setup

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the development server:**
    ```bash
    npm start
    ```

## Accessing the Application

*   **Frontend UI**: [http://localhost:3000](http://localhost:3000)
*   **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

Default admin credentials (if initial data was loaded):
*   **Email**: `admin@example.com`
*   **Password**: `password`

## Running Tests

To run the backend tests, execute the following command from the `backend` directory:
```bash
pytest
```

