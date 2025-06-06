# Forest Carbon Credit Estimation Tool - Project Summary

## 1. Project Overview

The Forest Carbon Credit Estimation Tool is a sophisticated, full-stack software system designed to calculate and manage forest carbon credit estimations, with a special focus on the ecosystems of Vietnam. The platform integrates a powerful FastAPI backend with a user-friendly React frontend, providing an end-to-end solution for project developers, environmental agencies, and researchers.

By combining geospatial data processing, satellite imagery analysis, and established carbon accounting methodologies (aligned with VCS and REDD+ principles), the tool delivers accurate and verifiable results, supporting efforts to combat climate change through forest conservation and restoration.

## 2. Key Features

-   **Full-Stack Application**: A secure, web-based platform with a clear separation between the backend API and the frontend user interface.
-   **User and Project Management**: Secure authentication, role-based access control, and a structured hierarchy for managing carbon projects.
-   **Geospatial Data Management**: Ingestion and management of project boundaries and forest areas using standard GeoJSON formats, all powered by a PostGIS database.
-   **Imagery Processing Pipeline**: An automated pipeline to process satellite or drone imagery, including validation, forest detection, and type classification using HSV color-space analysis.
-   **End-to-End Carbon Calculation**: A comprehensive module that calculates biomass, carbon stock, and net creditable carbon credits based on field data, allometric equations, and standard carbon science principles.
-   **Containerized and Scalable**: Deployed with Docker and Docker Compose for easy setup, consistency across environments, and scalability.

## 3. Technical Architecture

The system is built on a robust and modern technology stack:

-   **Backend**: The core business logic resides in a **FastAPI** application, which handles all API requests, data processing, and database interactions. It includes specialized modules for:
    -   `Geospatial Processing`: Leveraging libraries like GeoPandas and Rasterio for spatial analysis.
    -   `Image Processing`: Using OpenCV for HSV-based image classification.
    -   `Carbon Calculation`: Implementing the scientific formulas for biomass and carbon estimation.
-   **Frontend**: The user interface is a single-page application built with **React** and **TypeScript**, using Material-UI (MUI) for a clean and responsive design.
-   **Database**: **PostgreSQL** with the **PostGIS** extension serves as the data backbone, providing powerful capabilities for querying both standard and geospatial data.

For a detailed breakdown of the architecture, code structure, and API endpoints, please refer to the [Developer Guide](developer_guide.md).

## 4. Getting Started

To get the application up and running for local development, please follow the detailed instructions in the main [README.md](../README.md) file. For instructions on how to use the application's features, please consult the [User Guide](user_guide.md).

## 5. Conclusion

The Forest Carbon Credit Estimation Tool is a comprehensive, production-ready solution that successfully translates complex scientific methodologies into a practical, user-friendly application. It provides a solid foundation for managing forest carbon projects and can be extended to incorporate new methodologies and features in the future. The project's core strength lies in its robust architecture, data-driven processing pipelines, and adherence to established standards in carbon accounting.
