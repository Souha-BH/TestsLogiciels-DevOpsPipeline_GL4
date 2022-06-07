# Devops and Software Testing Project GL4

## App to test
A simple application for fetching and inserting musicians using Rest API to demonstrate the examples of unit test, and integration test.


### Technologies used
- `FastAPI` and `uvicorn` for Rest API
- `unittest` for assertions and mocks
- `testcontainers` to initialize local-database for integration tests
- `Flask` for MockServer
- `pandas` for all dataframe operations
- `psycopg2` to create a connection

## CI/CD pipeline
The main workflow consists of 2 jobs: Build(Test included) and Deploy to ECS.

## Testing
I've implemented 5 unit tests: [Unit tests](https://github.com/Souha-BH/TestsLogiciels-DevOpsPipeline_GL4/blob/master/app/unit_test.py) and 3 integration tests: [Integration tests](https://github.com/Souha-BH/TestsLogiciels-DevOpsPipeline_GL4/blob/master/app/integration_test.py)

### To run all tests
```bash
pytest 
```