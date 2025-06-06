-- Create Schemas
CREATE SCHEMA IF NOT EXISTS user_mgmt;
CREATE SCHEMA IF NOT EXISTS project_mgmt;
CREATE SCHEMA IF NOT EXISTS spatial;
CREATE SCHEMA IF NOT EXISTS imagery_data;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS calculation;

-- Create ENUM Types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstatus') THEN
        CREATE TYPE projectstatus AS ENUM ('Draft', 'Active', 'Completed', 'Archived');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'imagerysourceenum') THEN
        CREATE TYPE imagerysourceenum AS ENUM ('Satellite', 'Drone', 'Uploaded');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'imagerystatusenum') THEN
        CREATE TYPE imagerystatusenum AS ENUM ('Pending', 'Received', 'Validating', 'Preprocessing', 'Ready', 'Error');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'foresttypeenum') THEN
        CREATE TYPE foresttypeenum AS ENUM ('Tropical evergreen', 'Deciduous', 'Mangrove', 'Bamboo', 'Other');
    END IF;
END$$;

-- User Management Schema
CREATE TABLE IF NOT EXISTS user_mgmt.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_mgmt.permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_mgmt.role_permissions (
    role_id INTEGER NOT NULL REFERENCES user_mgmt.roles(role_id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES user_mgmt.permissions(permission_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_mgmt.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    organization VARCHAR(100),
    role_id INTEGER REFERENCES user_mgmt.roles(role_id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Reference Schema
CREATE TABLE IF NOT EXISTS reference.allometric_equations (
    equation_id SERIAL PRIMARY KEY,
    equation_name VARCHAR(255) NOT NULL,
    equation_formula VARCHAR(500) NOT NULL,
    region VARCHAR(100),
    species_group VARCHAR(100),
    source TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS reference.tree_species (
    species_id SERIAL PRIMARY KEY,
    scientific_name VARCHAR(150) UNIQUE NOT NULL,
    common_name_en VARCHAR(150),
    common_name_vi VARCHAR(150),
    wood_density NUMERIC(6, 4),
    default_allometric_equation_id INTEGER REFERENCES reference.allometric_equations(equation_id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Project Management Schema
CREATE TABLE IF NOT EXISTS project_mgmt.projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    status projectstatus DEFAULT 'Draft' NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES user_mgmt.users(user_id),
    location_geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_projects_location_geometry ON project_mgmt.projects USING gist (location_geometry);


-- Spatial Schema
CREATE TABLE IF NOT EXISTS spatial.forest_boundaries (
    forest_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    forest_name VARCHAR(100),
    forest_type VARCHAR(50),
    description TEXT,
    geometry GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    area_ha NUMERIC(12, 2),
    valid_from TIMESTAMPTZ DEFAULT now(),
    valid_to TIMESTAMPTZ,
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    source VARCHAR(100),
    source_date TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_forest_boundaries_geometry ON spatial.forest_boundaries USING gist (geometry);


CREATE TABLE IF NOT EXISTS spatial.forest_plots (
    plot_id SERIAL PRIMARY KEY,
    forest_id INTEGER NOT NULL REFERENCES spatial.forest_boundaries(forest_id) ON DELETE CASCADE,
    plot_name VARCHAR(150),
    geometry GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    CONSTRAINT enforce_valid_plot_geometry CHECK (ST_IsValid(geometry))
);
CREATE INDEX IF NOT EXISTS idx_forest_plots_geometry ON spatial.forest_plots USING gist (geometry);


CREATE TABLE IF NOT EXISTS spatial.plot_composition (
    plot_composition_id SERIAL PRIMARY KEY,
    plot_id INTEGER NOT NULL REFERENCES spatial.forest_plots(plot_id) ON DELETE CASCADE,
    species_id INTEGER NOT NULL REFERENCES reference.tree_species(species_id) ON DELETE RESTRICT,
    percentage_cover NUMERIC(5, 2),
    stem_density NUMERIC(10, 2),
    average_dbh NUMERIC(8, 2),
    average_height NUMERIC(8, 2),
    measurement_date DATE NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by INTEGER REFERENCES user_mgmt.users(user_id),
    CONSTRAINT check_percentage_cover_range CHECK (percentage_cover >= 0 AND percentage_cover <= 100),
    UNIQUE (plot_id, species_id, measurement_date)
);

-- Imagery Data Schema
CREATE TABLE IF NOT EXISTS imagery_data.imagery (
    imagery_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    source imagerysourceenum NOT NULL,
    source_identifier VARCHAR(255),
    acquisition_date TIMESTAMPTZ NOT NULL,
    sensor_type VARCHAR(100),
    resolution_m FLOAT,
    cloud_cover_percent FLOAT,
    file_path VARCHAR(1024) NOT NULL,
    file_format VARCHAR(50),
    crs VARCHAR(100),
    status imagerystatusenum DEFAULT 'Received' NOT NULL,
    processing_log TEXT,
    uploaded_by_id INTEGER REFERENCES user_mgmt.users(user_id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Calculation Schema
CREATE TABLE IF NOT EXISTS calculation.biomass (
    biomass_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    plot_id INTEGER REFERENCES spatial.forest_plots(plot_id) ON DELETE SET NULL,
    species_id INTEGER REFERENCES reference.tree_species(species_id) ON DELETE SET NULL,
    calculation_level VARCHAR(20) NOT NULL DEFAULT 'forest',
    calculation_date TIMESTAMPTZ DEFAULT now(),
    agb_per_ha NUMERIC(12, 2),
    agb_total NUMERIC(15, 2),
    bgb_total NUMERIC(15, 2),
    total_biomass NUMERIC(15, 2),
    allometric_equation_details VARCHAR(255),
    parameters JSON,
    uncertainty NUMERIC(5, 2),
    created_by INTEGER REFERENCES user_mgmt.users(user_id)
);

CREATE TABLE IF NOT EXISTS calculation.carbon_stock (
    carbon_id SERIAL PRIMARY KEY,
    biomass_id INTEGER NOT NULL UNIQUE REFERENCES calculation.biomass(biomass_id),
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    plot_id INTEGER REFERENCES spatial.forest_plots(plot_id) ON DELETE SET NULL,
    species_id INTEGER REFERENCES reference.tree_species(species_id) ON DELETE SET NULL,
    calculation_level VARCHAR(20) NOT NULL DEFAULT 'forest',
    calculation_date TIMESTAMPTZ DEFAULT now(),
    agb_carbon NUMERIC(15, 2),
    bgb_carbon NUMERIC(15, 2),
    total_carbon NUMERIC(15, 2),
    carbon_density NUMERIC(8, 2),
    agb_co2e NUMERIC(15, 2),
    bgb_co2e NUMERIC(15, 2),
    total_co2e NUMERIC(15, 2),
    uncertainty NUMERIC(5, 2),
    created_by INTEGER REFERENCES user_mgmt.users(user_id)
);

CREATE TABLE IF NOT EXISTS calculation.baseline (
    baseline_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    plot_id INTEGER REFERENCES spatial.forest_plots(plot_id) ON DELETE SET NULL,
    species_id INTEGER REFERENCES reference.tree_species(species_id) ON DELETE SET NULL,
    calculation_level VARCHAR(20) NOT NULL DEFAULT 'forest',
    reference_period_start DATE,
    reference_period_end DATE,
    baseline_type VARCHAR(50),
    baseline_carbon NUMERIC(15, 2),
    baseline_co2e NUMERIC(15, 2),
    parameters JSON,
    uncertainty NUMERIC(5, 2),
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by INTEGER REFERENCES user_mgmt.users(user_id)
);

CREATE TABLE IF NOT EXISTS calculation.carbon_credits (
    credit_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES project_mgmt.projects(project_id),
    forest_id INTEGER REFERENCES spatial.forest_boundaries(forest_id),
    plot_id INTEGER REFERENCES spatial.forest_plots(plot_id) ON DELETE SET NULL,
    species_id INTEGER REFERENCES reference.tree_species(species_id) ON DELETE SET NULL,
    carbon_id INTEGER NOT NULL REFERENCES calculation.carbon_stock(carbon_id),
    baseline_id INTEGER NOT NULL REFERENCES calculation.baseline(baseline_id),
    calculation_level VARCHAR(20) NOT NULL DEFAULT 'forest',
    calculation_date TIMESTAMPTZ DEFAULT now(),
    emission_reduction NUMERIC(15, 2),
    emission_reduction_co2e NUMERIC(15, 2),
    buffer_percentage NUMERIC(5, 2),
    buffer_amount NUMERIC(15, 2),
    leakage_factor NUMERIC(5, 4),
    leakage_deduction NUMERIC(15, 2),
    uncertainty_deduction NUMERIC(15, 2),
    creditable_amount NUMERIC(15, 2),
    methodology VARCHAR(50),
    uncertainty NUMERIC(5, 2),
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_by INTEGER REFERENCES user_mgmt.users(user_id),
    verified_at TIMESTAMPTZ,
    created_by INTEGER REFERENCES user_mgmt.users(user_id)
); 