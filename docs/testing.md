# Testing Documentation

## 1. Overview

This document outlines the testing strategy, scope, and instructions for running tests for the Forest Carbon Estimation Tool. The testing framework is designed to ensure code quality, functionality, and reliability across both the frontend and backend components of the application.

## 2. Testing Frameworks

The project utilizes a standard set of modern testing frameworks:

-   **Backend (Python)**:
    -   **`pytest`**: The primary framework for writing and running unit and integration tests. It is used for its powerful fixture model, concise syntax, and extensive plugin ecosystem.
-   **Frontend (TypeScript/React)**:
    -   **`Jest`**: The test runner for executing frontend tests.
    -   **`React Testing Library`**: The library used for testing React components in a way that resembles how users interact with them, focusing on behavior rather than implementation details.

## 3. Test Scope and Coverage

### Backend Tests

The backend test suite is located in the `tests/` directory and focuses on the core business logic.

-   **CRUD Operations (`/tests/crud/`)**: Tests for the data access layer, ensuring that database queries for creating, reading, updating, and deleting records behave as expected.
-   **API Endpoints (`/tests/api/`)**: Integration tests that target the API endpoints. These tests use a test client to simulate HTTP requests and verify responses, authentication, and authorization logic.
-   **Processing Modules (`/tests/processing/`)**: Unit tests for the data processing pipelines, which are critical for the application's core functionality:
    -   `test_image_processor.py`: Verifies the HSV color-based classification, seasonal adjustments, and other image analysis functions.
    -   `test_geospatial_processor.py`: Tests geometry transformations, area calculations, and other geospatial operations.
    -   `test_carbon_calculator.py`: Validates the biomass, carbon stock, and credit calculation formulas against expected outputs.
-   **Models and Schemas (`/tests/models/`, `/tests/schemas/`)**: Tests to ensure data models and validation schemas are correctly defined.

### Frontend Tests

Frontend tests are co-located with the components they test and focus on verifying the behavior and rendering of the UI.

-   **Component Tests**: Unit tests for individual React components to ensure they render correctly given different props.
-   **Integration Tests**: Tests for pages or complex components that involve user interactions (e.g., filling out a form, clicking buttons) and verify that the UI updates as expected.
    -   `Login.test.tsx`: Tests the login form validation and authentication flow.
    -   `Dashboard.test.tsx`: Ensures the main dashboard components render correctly.
    -   `ProjectList.test.tsx`: Tests the display of projects and user interactions like searching and opening dialogs.

## 4. Running Tests

### Backend Tests

To run the backend test suite, navigate to the `backend/` directory and execute `pytest`.

```bash
cd backend/
pytest
```

To run a specific test file and see verbose output:

```bash
pytest -v tests/processing/test_carbon_calculator.py
```

To generate a test coverage report:

```bash
pytest --cov=app
```

### Frontend Tests

To run the frontend tests, navigate to the `frontend/` directory and use the `npm test` script.

```bash
cd frontend/
npm test
```

This will launch the Jest test runner in interactive watch mode. Press `a` to run all tests.

## 5. Testing Strategy

-   **Unit Tests**: Form the base of the testing pyramid. They are used to test individual functions and components in isolation. For the backend, this means testing CRUD functions and processing logic with mocked dependencies. For the frontend, it means testing individual React components.
-   **Integration Tests**: Test the interaction between different parts of the system. In the backend, this involves testing API endpoints with a test database to ensure the full request-response cycle works. In the frontend, this involves testing that multiple components work together correctly on a single page.
-   **Test Data**: Tests use a combination of mock data (e.g., for simulating API responses in the frontend) and fixture data (e.g., predefined GeoJSON files for geospatial tests) to ensure consistency and reliability.

## 6. Future Test Enhancements

As the project matures, the following testing areas should be considered for expansion:

1.  **End-to-End (E2E) Tests**: Implement a framework like Cypress or Playwright to simulate full user journeys through the application in a browser.
2.  **Performance and Load Testing**: Use tools like `locust` or `k6` to test the backend's performance under heavy load, especially for the calculation and imagery processing endpoints.
3.  **Database Migration Tests**: Add tests to verify that Alembic migrations run correctly and do not corrupt data.
4.  **Security Testing**: Incorporate security scanning tools to identify potential vulnerabilities in both the frontend and backend code.

## Test Environment

- **Backend**: The `pytest` suite is configured to run against a dedicated test database, as defined by the `TEST_DATABASE_URL` in the `.env` file. Docker must be running to provide the PostgreSQL/PostGIS service.
- **Frontend**: The `Jest` tests run locally and mock any calls to the backend API, so no running backend is required.

## Test Data

The tests use a combination of:

- **Mock Data**: Simulated responses for API calls and database queries.
- **Fixture Data**: Predefined test data (e.g., GeoJSON files) for consistent test execution.
- **Generated Data**: Dynamically created test data to cover various scenarios and edge cases.

## Test Maintenance

When adding new features or modifying existing ones:

1. Update or add corresponding tests.
2. Ensure test coverage remains high.
3. Run the full test suite before committing changes.
4. Document any new test patterns or requirements.
