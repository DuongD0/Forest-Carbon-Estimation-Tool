# Forest Carbon Credit Estimation Tool

A comprehensive web-based platform for estimating and managing forest carbon credits in Vietnam. This tool combines satellite/drone imagery analysis, advanced computer vision, and geospatial data processing to provide accurate carbon credit calculations. It includes a peer-to-peer marketplace for carbon credit trading.

## Key Features

### Core Functionality
- **User Management & Authentication**: Secure Auth0-based authentication with role-based access control
- **Project Management**: Create and manage forest carbon projects with geospatial boundaries
- **Geospatial Data Processing**: Upload and manage project areas using GeoJSON polygons with PostGIS support
- **Forest Detection & Analysis**: AI-powered forest detection using OpenCV and HSV color signatures
- **Carbon Credit Calculation**: Scientific carbon estimation pipeline including:
  - Biomass calculation using allometric equations
  - Carbon stock derivation from biomass
  - Baseline scenario establishment
  - Net creditable carbon credit quantification
- **VCS Serial Number Generation**: Automated generation of Verified Carbon Standard serial numbers

### Marketplace Features
- **P2P Carbon Credit Trading**: Buy and sell carbon credits directly between users
- **Stripe Payment Integration**: Secure payment processing for transactions
- **Transaction Management**: Complete transaction history and status tracking

### Additional Features
- **Project Bookmarking**: Save and track favorite projects
- **Export Functionality**: Export project data and reports
- **Analytics & Reporting**: Track user activities and generate reports
- **Multi-Ecosystem Support**: Configurable carbon and biomass factors for different ecosystems

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS extension + Redis for caching
- **ORM**: SQLAlchemy with GeoAlchemy2
- **Authentication**: Auth0 integration
- **Payment Processing**: Stripe
- **Image Processing**: OpenCV
- **Geospatial**: Shapely, GeoPandas, Fiona
- **Data Validation**: Pydantic
- **Database Migrations**: Alembic

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Components**: Material-UI (MUI)
- **Authentication**: Auth0 React SDK
- **Data Fetching**: SWR + Axios
- **Routing**: React Router v6

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Uvicorn (ASGI)

## Project Structure

```
Forest-Carbon-Estimation-Tool/
├── backend/                    # FastAPI backend application
│   ├── alembic/               # Database migrations
│   │   └── versions/          # Migration scripts
│   ├── app/
│   │   ├── api/               # API layer
│   │   │   ├── endpoints/     # API endpoints
│   │   │   │   ├── bookmarks.py
│   │   │   │   ├── calculate.py
│   │   │   │   ├── ecosystems.py
│   │   │   │   ├── export.py
│   │   │   │   ├── geospatial.py
│   │   │   │   ├── p2p.py
│   │   │   │   ├── projects.py
│   │   │   │   └── users.py
│   │   │   └── deps.py        # API dependencies
│   │   ├── core/              # Core configuration
│   │   ├── crud/              # Database operations
│   │   ├── db/                # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   │       ├── carbon_calculator.py
│   │       ├── forest_detector.py
│   │       ├── serial_generator.py
│   │       └── stripe.py
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── contexts/          # React contexts
│   │   ├── pages/             # Page components
│   │   │   ├── CarbonCalculation.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ForestDetail.tsx
│   │   │   ├── ImageUploadPage.tsx
│   │   │   ├── ImageryDetail.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Marketplace.tsx
│   │   │   ├── ProjectDetail.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   └── Reports.tsx
│   │   ├── services/          # API services
│   │   └── types.ts           # TypeScript types
│   └── package.json
├── production/                # Production configs
├── scripts/                   # Utility scripts
├── tests/                     # Integration tests
└── docker-compose.yml        # Docker composition
```

## Database Schema

The application uses PostgreSQL with multiple schemas for better organization:
- **carbon_mgmt**: Carbon credits and ecosystem data
- **user_mgmt**: Users and bookmarks
- **project_mgmt**: Projects with geospatial data
- **p2p_marketplace**: Listings and transactions
- **analytics**: Event tracking

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 16+ (for frontend development)
- Conda (recommended for Python environment management)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Forest-Carbon-Estimation-Tool
   ```

2. **Create environment file**
   Create a `.env` file in the backend directory:
   ```bash
   # Database
   DATABASE_URL=postgresql://forest_user:forest_password@db:5432/forest_carbon_db
   REDIS_URL=redis://redis:6379/0
   
   # Security
   SECRET_KEY=your_super_secret_key_here
   
   # Auth0
   AUTH0_DOMAIN=your-auth0-domain
   AUTH0_API_AUDIENCE=your-api-audience
   AUTH0_ISSUER=https://your-auth0-domain/
   AUTH0_ALGORITHMS=RS256
   
   # Stripe
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_API_VERSION=2022-11-15
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Load initial data (optional)**
   ```bash
   docker-compose exec backend python -m app.db.initial_data
   ```

### Manual Setup (for development)

#### Backend Setup

1. **Create and activate conda environment**
   ```bash
   conda create -n Forest python=3.9
   conda activate Forest
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379

## Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## API Documentation

The API documentation is automatically generated and available at `/docs` when the backend is running. Key endpoints include:

- `/api/v1/users` - User management
- `/api/v1/projects` - Project CRUD operations
- `/api/v1/calculate` - Carbon calculation endpoints
- `/api/v1/ecosystems` - Ecosystem data management
- `/api/v1/p2p` - Marketplace operations
- `/api/v1/geospatial` - Geospatial data processing

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

[Add your license information here]

