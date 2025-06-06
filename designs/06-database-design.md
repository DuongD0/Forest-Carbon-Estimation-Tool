# Database Design and Data Management

## Overview

The Database Design and Data Management component is the foundation for storing, retrieving, and maintaining all data in the Forest Carbon Credit Estimation Tool. This design implements a geospatially-enabled database that efficiently handles satellite imagery metadata, forest boundaries, calculation results, and audit trails required for regulatory compliance. The system uses PostgreSQL with PostGIS extensions as its primary database technology.

## Functional Requirements

### Primary Functions
1. **Geospatial Data Storage**: Store and query vector and raster spatial data
2. **Calculation Results Management**: Maintain all carbon calculation results
3. **User and Project Management**: Handle user accounts and project information
4. **Version History**: Track changes to forest boundaries and calculations
5. **Audit Trail**: Maintain comprehensive logs for regulatory compliance
6. **Data Validation**: Ensure data integrity and consistency

### Performance Requirements
- Support for databases up to 10TB in size
- Spatial query performance under 2 seconds for typical operations
- Concurrent access by up to 100 users
- Transaction processing of up to 1,000 operations per minute
- High availability with 99.9% uptime

## Database Architecture

### Logical Data Model

```
┌──────────────────────────────────────────────────────────┐
│                    Data Model Overview                    │
│                                                          │
│  ┌────────────┐   ┌────────────┐      ┌────────────┐     │
│  │   User     │───│  Project   │──────│  Forest    │     │
│  │   Data     │   │   Data     │      │   Data     │     │
│  └────────────┘   └────────────┘      └────────────┘     │
│        │               │                    │            │
│        │               │                    │            │
│        ▼               ▼                    ▼            │
│  ┌────────────┐   ┌────────────┐      ┌────────────┐     │
│  │ Calculation│   │  Baseline  │──────│  Spatial   │     │
│  │  Results   │───│   Data     │      │  Reference │     │
│  └────────────┘   └────────────┘      └────────────┘     │
│        │               │                    │            │
│        │               │                    │            │
│        ▼               ▼                    ▼            │
│  ┌────────────┐   ┌────────────┐      ┌────────────┐     │
│  │  Audit     │   │ Reference  │      │  System    │     │
│  │   Logs     │   │   Data     │      │ Parameters │     │
│  └────────────┘   └────────────┘      └────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### Physical Database Structure

```
PostgreSQL Database Server
│
├── Schemas
│   ├── public          # System tables
│   ├── spatial         # Geospatial data
│   ├── calculation     # Carbon calculation data
│   ├── user_mgmt       # User management
│   ├── audit           # Audit logging
│   └── reference       # Reference data
│
├── Extensions
│   ├── PostGIS         # Spatial capabilities
│   ├── pgcrypto        # Encryption functions
│   ├── temporal_tables # Temporal data support
│   └── pg_stat_statements # Query statistics
│
├── Tablespaces
│   ├── primary_space   # Primary data storage
│   ├── spatial_space   # Optimized for spatial data
│   ├── index_space     # Index storage
│   └── archive_space   # Historical data
│
└── Backup and Recovery
    ├── WAL archiving   # Write-ahead log
    ├── Daily backups   # Full database dumps
    └── Point-in-time recovery # Recovery options
```

## Database Schema Design

### User Management Schema

```sql
CREATE SCHEMA user_mgmt;

-- Users table
CREATE TABLE user_mgmt.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    organization VARCHAR(100),
    role_id INTEGER REFERENCES user_mgmt.roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
CREATE TABLE user_mgmt.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE user_mgmt.permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Role permissions junction table
CREATE TABLE user_mgmt.role_permissions (
    role_id INTEGER REFERENCES user_mgmt.roles(role_id),
    permission_id INTEGER REFERENCES user_mgmt.permissions(permission_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- User sessions table
CREATE TABLE user_mgmt.sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id INTEGER REFERENCES user_mgmt.users(user_id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Project Management Schema

```sql
CREATE SCHEMA project_mgmt;

-- Projects table
CREATE TABLE project_mgmt.projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES user_mgmt.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    methodology_id INTEGER REFERENCES reference.methodologies(methodology_id),
    baseline_type VARCHAR(50),
    crediting_period INTEGER -- In years
);

-- Project participants junction table
CREATE TABLE project_mgmt.project_participants (
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    user_id INTEGER REFERENCES user_mgmt.users(user_id),
    role VARCHAR(50), -- Project-specific role (different from system role)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id)
);

-- Project documents table
CREATE TABLE project_mgmt.documents (
    document_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    document_name VARCHAR(100) NOT NULL,
    document_type VARCHAR(50),
    file_path TEXT NOT NULL,
    uploaded_by INTEGER REFERENCES user_mgmt.users(user_id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version VARCHAR(20),
    description TEXT
);
```

### Spatial Data Schema

```sql
CREATE SCHEMA spatial;

-- Forest boundaries table
CREATE TABLE spatial.forest_boundaries (
    forest_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    forest_name VARCHAR(100),
    forest_type VARCHAR(50),
    geometry GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    area_ha NUMERIC(12, 2),
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100), -- Source of the spatial data
    source_date DATE, -- Date of the source data
    CONSTRAINT enforce_valid_geometry CHECK (ST_IsValid(geometry))
);

-- Create spatial index
CREATE INDEX forest_boundaries_geom_idx ON spatial.forest_boundaries USING GIST (geometry);

-- Satellite imagery metadata table
CREATE TABLE spatial.imagery_metadata (
    imagery_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    image_name VARCHAR(100) NOT NULL,
    acquisition_date DATE,
    sensor VARCHAR(50),
    resolution NUMERIC(8, 2), -- In meters
    cloud_cover NUMERIC(5, 2), -- Percentage
    file_path TEXT,
    bounds GEOMETRY(POLYGON, 4326),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES user_mgmt.users(user_id)
);

-- Create spatial index for imagery bounds
CREATE INDEX imagery_bounds_idx ON spatial.imagery_metadata USING GIST (bounds);

-- Forest classification results table
CREATE TABLE spatial.forest_classification (
    classification_id SERIAL PRIMARY KEY,
    imagery_id INTEGER REFERENCES spatial.imagery_metadata(imagery_id),
    forest_type VARCHAR(50),
    confidence NUMERIC(5, 2), -- Percentage
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    area_ha NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    algorithm VARCHAR(50),
    parameters JSONB -- Algorithm parameters
);

-- Create spatial index
CREATE INDEX forest_classification_geom_idx ON spatial.forest_classification USING GIST (geometry);
```

### Calculation Schema

```sql
CREATE SCHEMA calculation;

-- Biomass calculation results
CREATE TABLE calculation.biomass (
    biomass_id SERIAL PRIMARY KEY,
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    calculation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agb_per_ha NUMERIC(12, 2), -- Above-ground biomass per hectare
    agb_total NUMERIC(15, 2), -- Total above-ground biomass
    bgb_total NUMERIC(15, 2), -- Total below-ground biomass
    total_biomass NUMERIC(15, 2), -- Total biomass
    allometric_equation VARCHAR(100),
    parameters JSONB, -- Equation parameters
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    uncertainty NUMERIC(5, 2) -- Percentage
);

-- Carbon stock calculation results
CREATE TABLE calculation.carbon_stock (
    carbon_id SERIAL PRIMARY KEY,
    biomass_id INTEGER REFERENCES calculation.biomass(biomass_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    calculation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agb_carbon NUMERIC(15, 2), -- Above-ground carbon
    bgb_carbon NUMERIC(15, 2), -- Below-ground carbon
    total_carbon NUMERIC(15, 2), -- Total carbon
    carbon_density NUMERIC(8, 2), -- Carbon per hectare
    agb_co2e NUMERIC(15, 2), -- CO2 equivalent for AGB
    bgb_co2e NUMERIC(15, 2), -- CO2 equivalent for BGB
    total_co2e NUMERIC(15, 2), -- Total CO2 equivalent
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    uncertainty NUMERIC(5, 2) -- Percentage
);

-- Baseline data table
CREATE TABLE calculation.baseline (
    baseline_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    reference_period_start DATE,
    reference_period_end DATE,
    baseline_type VARCHAR(50),
    baseline_carbon NUMERIC(15, 2), -- Baseline carbon stock
    baseline_co2e NUMERIC(15, 2), -- Baseline CO2 equivalent
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    parameters JSONB, -- Baseline calculation parameters
    uncertainty NUMERIC(5, 2) -- Percentage
);

-- Carbon credit calculation results
CREATE TABLE calculation.carbon_credits (
    credit_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    carbon_id INTEGER REFERENCES calculation.carbon_stock(carbon_id),
    baseline_id INTEGER REFERENCES calculation.baseline(baseline_id),
    calculation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    emission_reduction NUMERIC(15, 2), -- Emission reduction in carbon
    emission_reduction_co2e NUMERIC(15, 2), -- Emission reduction in CO2e
    buffer_percentage NUMERIC(5, 2), -- Buffer percentage
    buffer_amount NUMERIC(15, 2), -- Buffer amount in CO2e
    creditable_amount NUMERIC(15, 2), -- Creditable amount in CO2e
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    methodology VARCHAR(50),
    uncertainty NUMERIC(5, 2), -- Percentage
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_by INTEGER REFERENCES user_mgmt.users(user_id),
    verified_at TIMESTAMP WITH TIME ZONE
);
```

### Audit Schema

```sql
CREATE SCHEMA audit;

-- System audit log
CREATE TABLE audit.system_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_mgmt.users(user_id),
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    action_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    details JSONB
);

-- Create index on timestamp for log queries
CREATE INDEX system_log_timestamp_idx ON audit.system_log (action_timestamp);

-- Calculation audit log
CREATE TABLE audit.calculation_log (
    log_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    calculation_type VARCHAR(50),
    calculation_id INTEGER,
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parameters JSONB,
    results JSONB,
    duration INTEGER -- In milliseconds
);

-- Verification log
CREATE TABLE audit.verification_log (
    verification_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES project_mgmt.projects(project_id),
    credit_id INTEGER REFERENCES calculation.carbon_credits(credit_id),
    verified_by INTEGER REFERENCES user_mgmt.users(user_id),
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    comments TEXT,
    documentation_path TEXT
);
```

### Reference Schema

```sql
CREATE SCHEMA reference;

-- Carbon methodologies table
CREATE TABLE reference.methodologies (
    methodology_id SERIAL PRIMARY KEY,
    methodology_name VARCHAR(100) NOT NULL,
    version VARCHAR(20),
    description TEXT,
    organization VARCHAR(100), -- e.g., VCS, CDM, etc.
    documentation_url TEXT,
    parameters JSONB, -- Default parameters
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Allometric equations table
CREATE TABLE reference.allometric_equations (
    equation_id SERIAL PRIMARY KEY,
    equation_name VARCHAR(100) NOT NULL,
    forest_type VARCHAR(50),
    equation TEXT,
    parameters JSONB,
    source TEXT,
    region VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Wood density table
CREATE TABLE reference.wood_density (
    species_id SERIAL PRIMARY KEY,
    scientific_name VARCHAR(100),
    common_name VARCHAR(100),
    wood_density NUMERIC(5, 3), -- g/cm³
    forest_type VARCHAR(50),
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Administrative boundaries table
CREATE TABLE reference.admin_boundaries (
    boundary_id SERIAL PRIMARY KEY,
    boundary_name VARCHAR(100) NOT NULL,
    boundary_type VARCHAR(50), -- e.g., country, province, district
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    parent_id INTEGER REFERENCES reference.admin_boundaries(boundary_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX admin_boundaries_geom_idx ON reference.admin_boundaries USING GIST (geometry);
```

## Database Functions and Procedures

### Spatial Functions

```sql
-- Calculate area in hectares for a geometry in WGS84
CREATE OR REPLACE FUNCTION spatial.calculate_area_ha(geom GEOMETRY)
RETURNS NUMERIC AS $$
DECLARE
    area_ha NUMERIC;
BEGIN
    -- Transform to Vietnam Albers Equal Area projection for accurate area calculation
    area_ha := ST_Area(
        ST_Transform(
            geom,
            '+proj=aea +lat_1=8 +lat_2=23 +lat_0=15.5 +lon_0=106 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
        )
    ) / 10000; -- Convert m² to hectares
    
    RETURN area_ha;
END;
$$ LANGUAGE plpgsql;

-- Validate and repair forest geometry
CREATE OR REPLACE FUNCTION spatial.validate_forest_geometry(geom GEOMETRY)
RETURNS GEOMETRY AS $$
DECLARE
    valid_geom GEOMETRY;
BEGIN
    -- Check if geometry is valid
    IF ST_IsValid(geom) THEN
        valid_geom := geom;
    ELSE
        -- Try to make it valid
        valid_geom := ST_MakeValid(geom);
        
        -- Ensure it's a MultiPolygon
        IF GeometryType(valid_geom) != 'MULTIPOLYGON' THEN
            IF GeometryType(valid_geom) = 'POLYGON' THEN
                valid_geom := ST_Multi(valid_geom);
            ELSE
                -- Extract polygons if we got a GeometryCollection
                valid_geom := ST_CollectionExtract(valid_geom, 3);
            END IF;
        END IF;
    END IF;
    
    RETURN valid_geom;
END;
$$ LANGUAGE plpgsql;

-- Find forests within administrative boundary
CREATE OR REPLACE FUNCTION spatial.forests_within_boundary(boundary_id INTEGER)
RETURNS TABLE(forest_id INTEGER, forest_name VARCHAR, area_ha NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.forest_id, 
        f.forest_name, 
        f.area_ha
    FROM 
        spatial.forest_boundaries f,
        reference.admin_boundaries b
    WHERE 
        b.boundary_id = boundary_id
        AND ST_Intersects(f.geometry, b.geometry)
        AND (
            -- Forest must have at least 90% of its area within the boundary
            ST_Area(ST_Intersection(f.geometry, b.geometry)) > 0.9 * ST_Area(f.geometry)
        );
END;
$$ LANGUAGE plpgsql;
```

### Audit Functions

```sql
-- Trigger function for audit logging
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit.system_log(
            user_id, 
            action_type, 
            table_name, 
            record_id, 
            details
        )
        VALUES(
            current_setting('app.current_user_id', true)::INTEGER,
            'DELETE',
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            OLD.id,
            row_to_json(OLD)
        );
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit.system_log(
            user_id, 
            action_type, 
            table_name, 
            record_id, 
            details
        )
        VALUES(
            current_setting('app.current_user_id', true)::INTEGER,
            'UPDATE',
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            NEW.id,
            jsonb_build_object(
                'old', row_to_json(OLD),
                'new', row_to_json(NEW),
                'changed_fields', (
                    SELECT jsonb_object_agg(key, value)
                    FROM jsonb_each(to_jsonb(NEW))
                    WHERE to_jsonb(NEW)->key IS DISTINCT FROM to_jsonb(OLD)->key
                )
            )
        );
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit.system_log(
            user_id, 
            action_type, 
            table_name, 
            record_id, 
            details
        )
        VALUES(
            current_setting('app.current_user_id', true)::INTEGER,
            'INSERT',
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            NEW.id,
            row_to_json(NEW)
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### Calculation Functions

```sql
-- Get latest carbon calculation for a forest
CREATE OR REPLACE FUNCTION calculation.get_latest_carbon(forest_id INTEGER)
RETURNS TABLE(
    carbon_id INTEGER,
    calculation_date TIMESTAMP WITH TIME ZONE,
    total_carbon NUMERIC,
    total_co2e NUMERIC,
    carbon_density NUMERIC,
    uncertainty NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.carbon_id,
        c.calculation_date,
        c.total_carbon,
        c.total_co2e,
        c.carbon_density,
        c.uncertainty
    FROM 
        calculation.carbon_stock c
    WHERE 
        c.forest_id = forest_id
    ORDER BY 
        c.calculation_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Calculate project total carbon credits
CREATE OR REPLACE FUNCTION calculation.project_total_credits(project_id INTEGER)
RETURNS TABLE(
    total_creditable NUMERIC,
    total_buffer NUMERIC,
    average_uncertainty NUMERIC,
    forest_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        SUM(cc.creditable_amount) AS total_creditable,
        SUM(cc.buffer_amount) AS total_buffer,
        AVG(cc.uncertainty) AS average_uncertainty,
        COUNT(DISTINCT cc.forest_id) AS forest_count
    FROM 
        calculation.carbon_credits cc
    WHERE 
        cc.project_id = project_id;
END;
$$ LANGUAGE plpgsql;
```

## Database Indexing Strategy

### Primary Indexes

| Table | Index Type | Columns | Purpose |
|-------|------------|---------|---------|
| All tables | B-tree | Primary key | Primary key lookup |
| spatial.forest_boundaries | GiST | geometry | Spatial queries |
| spatial.imagery_metadata | GiST | bounds | Spatial queries |
| spatial.forest_classification | GiST | geometry | Spatial queries |
| reference.admin_boundaries | GiST | geometry | Spatial queries |
| audit.system_log | B-tree | action_timestamp | Time-based queries |

### Secondary Indexes

| Table | Index Type | Columns | Purpose |
|-------|------------|---------|---------|
| user_mgmt.users | B-tree | username, email | User lookup |
| project_mgmt.projects | B-tree | owner_id | Project filtering by owner |
| spatial.forest_boundaries | B-tree | project_id, forest_type | Filtering forests |
| calculation.carbon_stock | B-tree | forest_id, calculation_date | Time-series queries |
| calculation.carbon_credits | B-tree | project_id, verification_status | Credit verification |

## Data Access Patterns

### Common Queries

1. **Project Dashboard Query**
```sql
SELECT 
    p.project_id,
    p.project_name,
    p.status,
    COUNT(DISTINCT f.forest_id) AS forest_count,
    SUM(f.area_ha) AS total_area_ha,
    SUM(cc.creditable_amount) AS total_credits,
    AVG(cc.uncertainty) AS avg_uncertainty
FROM 
    project_mgmt.projects p
LEFT JOIN 
    spatial.forest_boundaries f ON p.project_id = f.project_id
LEFT JOIN 
    calculation.carbon_credits cc ON p.project_id = cc.project_id
WHERE 
    p.owner_id = :user_id
GROUP BY 
    p.project_id, p.project_name, p.status;
```

2. **Forest Details Query**
```sql
SELECT 
    f.forest_id,
    f.forest_name,
    f.forest_type,
    f.area_ha,
    c.total_carbon,
    c.total_co2e,
    c.carbon_density,
    b.baseline_carbon,
    cc.emission_reduction_co2e,
    cc.creditable_amount,
    cc.uncertainty
FROM 
    spatial.forest_boundaries f
LEFT JOIN 
    calculation.carbon_stock c ON f.forest_id = c.forest_id
LEFT JOIN 
    calculation.baseline b ON f.forest_id = b.forest_id
LEFT JOIN 
    calculation.carbon_credits cc ON f.forest_id = cc.forest_id
WHERE 
    f.forest_id = :forest_id;
```

3. **Spatial Query for Forests in Region**
```sql
SELECT 
    f.forest_id,
    f.forest_name,
    f.forest_type,
    f.area_ha,
    ST_AsGeoJSON(f.geometry) AS geometry
FROM 
    spatial.forest_boundaries f,
    reference.admin_boundaries b
WHERE 
    b.boundary_id = :boundary_id
    AND ST_Intersects(f.geometry, b.geometry);
```

## Data Validation and Integrity

### Database Constraints

1. **Primary Keys**: Ensure uniqueness of records
2. **Foreign Keys**: Maintain referential integrity
3. **Check Constraints**: Validate data ranges and formats
4. **Not Null Constraints**: Ensure required data is provided
5. **Unique Constraints**: Prevent duplicate values

### Validation Rules

1. **Geometry Validation**: All geometries must be valid according to OGC standards
2. **Area Calculation**: Area values must be recalculated when geometries change
3. **User Permissions**: Data modifications only allowed by authorized users
4. **Temporal Consistency**: Dates must be chronologically valid
5. **Project Constraints**: Projects must have valid owners and methodologies

## Transaction Management

### Transaction Isolation Levels

- **Read Committed**: Default level for most operations
- **Repeatable Read**: For report generation and calculations
- **Serializable**: For critical financial transactions

### Transaction Patterns

1. **Atomic Calculations**: All carbon calculations must be atomic
2. **Two-Phase Verification**: Credit verification requires approval workflow
3. **Audit Logging**: All transactions must generate audit logs
4. **Compensation Actions**: Fallback procedures for failed transactions

## Backup and Recovery Strategy

### Backup Schedule

1. **Transaction Logs**: Continuous archiving
2. **Incremental Backups**: Hourly
3. **Full Backups**: Daily
4. **Off-site Backups**: Weekly

### Recovery Procedures

1. **Point-in-Time Recovery**: Ability to restore to any point in time
2. **Disaster Recovery**: Complete rebuild from offsite backups
3. **Transaction Replay**: Ability to replay transactions after recovery
4. **Verification Process**: Data integrity checks after recovery

## Performance Optimization

### Query Optimization

1. **Explain Analysis**: Regular review of query execution plans
2. **Materialized Views**: For complex, frequently-accessed data
3. **Query Rewriting**: Optimization of suboptimal queries
4. **Partitioning**: Time-based partitioning for historical data

### Database Configuration

1. **Memory Allocation**: Proper sizing of shared_buffers and work_mem
2. **Autovacuum Settings**: Optimized for workload patterns
3. **Checkpoint Configuration**: Balanced for performance and recovery
4. **Connection Pooling**: Using PgBouncer for connection management

## Security Measures

### Access Control

1. **Row-Level Security**: Restrict access to specific rows based on user
2. **Column-Level Security**: Restrict access to sensitive columns
3. **Role-Based Access Control**: Define permissions by role
4. **Dynamic Privileges**: Adjust permissions based on context

### Data Protection

1. **Encryption at Rest**: Tablespace encryption for sensitive data
2. **Encrypted Connections**: SSL/TLS for all database connections
3. **Password Policies**: Strong password requirements
4. **Audit Trails**: Comprehensive logging of all access and changes

## Implementation Guidelines

### Development Standards

1. **SQL Style Guide**: Follow consistent SQL formatting
2. **Object Naming Conventions**: Standardized naming for tables and fields
3. **Version Control**: Database schema under version control
4. **Migration Scripts**: Incremental changes with up/down migrations

### Integration Points

1. **ORM Integration**: SQLAlchemy mappings for Python code
2. **API Layer**: GraphQL/REST API for data access
3. **Reporting Interface**: Dedicated read-only connections for reports
4. **ETL Processes**: Scheduled data integration workflows

This detailed documentation provides a comprehensive guide for implementing the Database Design and Data Management component, covering schema design, functions, and best practices for development teams.