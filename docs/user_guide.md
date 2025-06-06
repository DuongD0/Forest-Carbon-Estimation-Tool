# User Guide

## Introduction

Welcome to the Forest Carbon Estimation Tool! This application helps you manage forest carbon projects, process satellite imagery, and calculate carbon stocks and credits for forests in Vietnam. This guide will walk you through the key features and how to use them effectively.

## Getting Started

### System Requirements

- A modern web browser (Chrome, Firefox, Safari, or Edge).
- The application is deployed via Docker, so no local installation of Python or Node.js is required for users.

### Accessing the Application

Once the system is deployed and running, you can access it at the provided URL (e.g., `http://localhost:3000` for local development).

### First-time Login

If the initial data script has been run, you can use the following default administrator credentials for your first login:

-   **Email**: `admin@example.com`
-   **Password**: `password`

**Important**: It is highly recommended that you change the default password after your first login through the user profile page.

## Main Features

### Dashboard

The dashboard is the first page you see after logging in. It provides a high-level overview of your activities:

-   **Recent Projects**: A list of the most recently accessed projects for quick navigation.
-   **Recent Forests**: A list of recently viewed forest areas.
-   **Quick Actions**: Buttons to quickly start common tasks like creating a new project.

### Project Management

Projects are the top-level containers for your work. A project typically represents a single carbon accounting initiative.

#### Creating a Project

1.  From the dashboard or the "Projects" page, click "New Project".
2.  Fill in the required project details:
    -   **Project Name**: A descriptive name for your project.
    -   **Description**: (Optional) Details about the project's goals, location, and scope.
    -   **Location Geometry**: (Optional) Provide a GeoJSON Polygon to define the overall project boundary.
3.  Click "Create Project". You will be redirected to the new project's detail page.

#### Managing Projects

-   **View all projects** on the "Projects" list page.
-   **Search and filter** for projects.
-   Click on a project to view its **detail page**, which shows associated forests and calculation results.
-   From the detail page, you can **edit** or **delete** a project.

### Forest Management

Forests are the specific, delineated areas of woodland within a project where carbon stock will be measured.

#### Adding a Forest to a Project

1.  Navigate to a project's detail page.
2.  Click "Add Forest".
3.  Fill in the forest details:
    -   **Forest Name**: A unique identifier for the forest area (e.g., "Cuc Phuong National Park - Block A").
    -   **Forest Type**: Select the dominant forest type (e.g., Tropical evergreen, Mangrove).
    -   **Geometry**: Provide a GeoJSON MultiPolygon that defines the precise boundary of the forest area.
4.  Click "Save Forest".

### Imagery Management

The system uses satellite or drone imagery to analyze forest characteristics.

#### Uploading Imagery

1.  From a project's detail page, navigate to the "Imagery" tab and click "Upload Imagery".
2.  Fill in the imagery's metadata:
    -   **Project**: The project this imagery belongs to.
    -   **Acquisition Date**: The date the imagery was captured.
    -   **Sensor Type**: (Optional) The sensor used (e.g., Sentinel-2, Landsat 8, DJI Mavic).
    -   **Resolution (m)**: (Optional) The spatial resolution in meters.
3.  Select the imagery file (e.g., a GeoTIFF) to upload.
4.  Click "Upload". The imagery will be stored and linked to the project.

#### Processing Imagery

1.  Once an imagery record is created, navigate to its detail page.
2.  Click the **"Process"** button.
3.  The backend will initiate the full processing pipeline, which includes:
    -   Validation and preprocessing.
    -   Forest area detection.
    -   Forest type classification.
    -   Generation of result data.
4.  The status of the imagery will update to "Ready" when complete, or "Error" if issues occurred.

### Carbon Calculation

The core feature of the tool is to calculate carbon stocks and estimate potential carbon credits.

1.  Navigate to the detail page for the project you wish to analyze.
2.  Click the **"Run Calculation"** button.
3.  This triggers a background task that performs the full calculation pipeline for **all forests** within that project. The steps include:
    -   Aggregating plot data (if available) for each forest.
    -   Calculating total Above-Ground Biomass (AGB) and Below-Ground Biomass (BGB).
    -   Converting biomass to total carbon stock (tonnes C) and CO2 equivalent (tonnes CO2e).
    -   Establishing a baseline scenario for comparison.
    -   Quantifying the net creditable emissions reduction after accounting for leakage and risk buffers.
4.  The results will be displayed on the project's "Calculations" tab once the task is complete.

## User Management (Admin)

Administrators have the ability to manage system users and roles.

1.  Navigate to the "Users" or "Roles" page from the main menu.
2.  Here you can:
    -   View all users and roles in the system.
    -   Create new users and assign them a role.
    -   Edit user details or deactivate accounts.
    -   Create or update roles and their associated permissions.

## Troubleshooting

-   **Login Problems**: Ensure you are using the correct email and password. The default password is `password`, not `admin123`.
-   **Upload Fails**: Check that your file (e.g., for GeoJSON or imagery) is correctly formatted and not excessively large.
-   **Calculation Errors**: Verify that the project contains at least one forest with valid geometry. For detailed calculations, ensure forest plots and species data have been added.

## Glossary

-   **Project**: A high-level container for a carbon accounting initiative.
-   **Forest**: A specific, geographically delineated forest area within a project.
-   **Imagery**: Satellite or aerial imagery used for analysis.
-   **Allometric Equation**: A mathematical formula used to estimate tree biomass from inventory data (like diameter and height).
-   **Biomass**: The total mass of living organic material in an area, typically split into Above-Ground (AGB) and Below-Ground (BGB).
-   **Carbon Stock**: The amount of carbon stored in the forest's biomass.
-   **Carbon Credits**: Tradable certificates representing a certified reduction of greenhouse gases, where one credit equals one tonne of CO2 equivalent.
-   **Baseline**: A scenario that represents the anticipated greenhouse gas emissions in the absence of the project.
-   **Leakage**: The net change of greenhouse gas emissions that occurs outside the project boundary but is measurable and attributable to the project activity.
