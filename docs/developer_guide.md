# Developer Documentation

## Overview

This document provides comprehensive technical documentation for developers working on the Forest Carbon Estimation Tool. It covers the system architecture, key components, code organization, and development guidelines.

## System Architecture

The Forest Carbon Estimation Tool follows a modern, multi-tiered architecture with a clear separation of concerns between the frontend, backend, and database layers.

1.  **Frontend**: A responsive and interactive single-page application (SPA) built with React and TypeScript. It communicates with the backend via RESTful API calls.
2.  **Backend API**: A high-performance RESTful API service built with FastAPI. It handles business logic, data processing, user authentication, and database interactions.
3.  **Database**: A PostgreSQL database with the PostGIS extension to efficiently store and query both relational and complex geospatial data.
4.  **Processing Modules**: Integrated within the backend, these Python modules contain the core scientific and data processing logic for image analysis, geospatial calculations, and carbon credit estimation.

### Architecture Diagram

```mermaid
graph TD
    subgraph "User Interface"
        A[React Frontend <br/>(TypeScript, MUI)]
    end

    subgraph "Backend Service (FastAPI)"
        B[API Routers]
        subgraph "Core Logic"
            C[Processing Modules <br/>- ImageProcessor <br/>- GeospatialProcessor <br/>- CarbonCalculator]
            D[CRUD Operations <br/>(Data Access Layer)]
        end
        E[SQLAlchemy Models]
    end

    subgraph "Data Storage"
        F[PostgreSQL Database <br/>with PostGIS]
    end

    A -- REST API Calls --> B
    B -- Serves Data --> A
    B --> C
    B --> D
    D -- Uses --> E
    D -- Queries/ORM --> F
```

## Code Organization

### Backend Structure (`backend/`)

```
backend/
├── alembic/                # Database migration scripts
├── app/
│   ├── api/                # API endpoints
│   │   ├── endpoints/      # Route handlers by resource (users, projects, etc.)
│   │   └── api_v1.py       # Main API router configuration
│   ├── core/               # Core functionality (config, security)
│   ├── crud/               # Database CRUD operations (data access layer)
│   ├── db/                 # DB connection, session, base model, initial data
│   ├── models/             # SQLAlchemy ORM models
│   ├── processing/         # Core business logic modules
│   │   ├── image_processor.py
│   │   ├── geospatial_processor.py
│   │   └── carbon_calculator.py
│   └── schemas/            # Pydantic schemas for data validation
├── tests/                  # Pytest test suite
├── alembic.ini             # Alembic configuration
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

### Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── components/         # Reusable UI components (e.g., layout, dashboard widgets)
│   ├── contexts/           # React context providers (e.g., AuthContext)
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Top-level page components (e.g., Dashboard, ProjectDetail)
│   ├── services/           # API service clients for interacting with the backend
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main application component and routing setup
│   └── index.tsx           # Application entry point
├── package.json            # NPM dependencies and scripts
└── tsconfig.json           # TypeScript configuration
```

## API Endpoints

The API is versioned under `/api/v1`.

### Authentication (`/auth`)
- `POST /login/access-token`: User login, returns JWT access token.

### Users & Roles (`/users`)
- `POST /users/`: Create a new user (admin).
- `GET /users/`: Get a list of users (admin).
- `GET /users/me`: Get the current authenticated user's details.
- `GET /users/{user_id}`: Get a specific user's details (admin).
- `PUT /users/{user_id}`: Update a user (admin).
- `DELETE /users/{user_id}`: Delete a user (admin).
- `POST /roles/`: Create a new role (admin).
- `GET /roles/`: Get all roles (admin).

### Projects (`/projects`)
- `POST /`: Create a new project.
- `GET /`: List projects for the current user (or all for admin).
- `GET /{project_id}`: Get project details.
- `PUT /{project_id}`: Update a project.
- `DELETE /{project_id}`: Delete a project.
- `POST /{project_id}/calculate`: Trigger background carbon calculation for the project.

### Forests (`/forests`)
- `POST /`: Create a new forest area within a project.
- `GET /`: Get forests for a given `project_id`.
- `GET /{forest_id}`: Get forest details.
- `PUT /{forest_id}`: Update a forest's metadata or geometry.
- `DELETE /{forest_id}`: Delete a forest.

### Imagery (`/imagery`)
- `POST /upload/`: Upload an imagery file and its metadata for a project.
- `GET /`: Get imagery records for a given `project_id`.
- `GET /{imagery_id}`: Get imagery record details.
- `PUT /{imagery_id}`: Update imagery metadata.
- `DELETE /{imagery_id}`: Delete an imagery record.
- `POST /{imagery_id}/process`: Trigger the processing pipeline for an imagery file.

## Development Guidelines

### Backend Development

1.  **Environment Setup**:
    *   Use a Conda environment for consistency (`conda activate Forest`).
    *   Install dependencies: `pip install -r requirements.txt`.
    *   Create a `.env` file from `.env.example` and configure your database connection string.

2.  **Database Migrations**:
    *   To generate a new migration script after changing SQLAlchemy models:
        ```bash
        alembic revision --autogenerate -m "Your descriptive message"
        ```
    *   To apply migrations to the database:
        ```bash
        alembic upgrade head
        ```

3.  **Running the API**:
    *   Use Docker Compose for a full environment (recommended): `docker-compose up --build`
    *   Or run locally with Uvicorn: `uvicorn app.main:app --reload`

4.  **Testing**:
    *   Run the test suite: `pytest`
    *   Generate a coverage report: `pytest --cov=app`

### Frontend Development

1.  **Environment Setup**:
    *   Node.js v16+ and npm.
    *   Install dependencies: `npm install`.

2.  **Development Server**:
    *   Start the local dev server: `npm start`. The app will be available at `http://localhost:3000`.
    *   Build for production: `npm run build`.

3.  **API Integration**:
    *   The frontend uses an Axios instance for API calls, configured in `src/services/api.ts`.
    *   API service functions should be organized by resource (e.g., `projectService.ts`, `authService.ts`).

## Extending the Application

### Adding a New API Endpoint & CRUD Logic

1.  **Model**: Define or update the SQLAlchemy model in `app/models/`.
2.  **Schema**: Define the Pydantic schemas for request/response validation in `app/schemas/`.
3.  **CRUD**: Implement the database interaction logic in a new file in `app/crud/`. Import it in `app/crud/__init__.py`.
4.  **Endpoint**: Create the endpoint router in `app/api/endpoints/`.
5.  **Router**: Include the new endpoint router in `app/api/api_v1.py`.
6.  **Test**: Write tests for the new CRUD functions and API endpoint.

### Adding a New Frontend Page

1.  **Type Definitions**: Add any new TypeScript interfaces in `src/types/`.
2.  **API Service**: Create functions in `src/services/` to call the new backend endpoints.
3.  **Component/Page**: Create the new page component in `src/pages/`. Use components from `src/components/` for reusability.
4.  **Routing**: Add the new route to the router in `src/App.tsx`.
5.  **State Management**: If needed, use `React.Context` or a state management library to handle global state.

## Troubleshooting

-   **CORS Errors**: Ensure the frontend origin (`http://localhost:3000`) is listed in the `BACKEND_CORS_ORIGINS` in your backend's `.env` file.
-   **Database Connection Errors**: Double-check the `DATABASE_URL` in your `.env` file and ensure the PostgreSQL container is running.
-   **Alembic "Target metadata is not a dict"**: Ensure all new SQLAlchemy models are imported into `app/db/base.py` so that Alembic can detect them.
-   **Frontend `401 Unauthorized`**: Check that the `Authorization` header with the Bearer token is being sent correctly with API requests after login.
