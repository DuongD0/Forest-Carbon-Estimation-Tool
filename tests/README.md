# Backend Testing

This directory contains the backend tests for the Forest Carbon Estimation Tool.

## Running Tests

To run the tests, you will need to have the test database running. You can start it with Docker Compose:

```bash
docker-compose up -d db_test
```

Before running the tests, make sure you have installed all the dependencies, including the test dependencies:

```bash
pip install -r backend/requirements.txt
```

### PYTHONPATH

There is a known issue with the `PYTHONPATH` when running the tests. To work around this, you can set the `PYTHONPATH` explicitly when running `pytest`:

```bash
PYTHONPATH=. pytest
```

Alternatively, you can add the following to your shell's configuration file (e.g., `.bashrc`, `.zshrc`):

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/Forest-Carbon-Estimation-Tool"
```

### Running the Tests

Once you have the database running and the `PYTHONPATH` set, you can run the tests from the root of the project:

```bash
pytest
```

You can also run specific tests:

```bash
pytest tests/test_api.py
``` 