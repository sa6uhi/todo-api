# ToDo API

A RESTful API for managing a task list (ToDo list) built with **FastAPI**, **PostgreSQL**, and **JWT authentication**. This project provides a fully functional API with CRUD operations for tasks, user authentication, pagination, and unit tests. The application is Dockerized for easy deployment and includes comprehensive documentation.

## Table of Contents
- [Project Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Running Tests](#running-tests)
  - [Local Environment](#local-environment)
  - [Docker Environment](#docker-environment)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [User Endpoints](#user-endpoints)
  - [Task Endpoints](#task-endpoints)
  - [Example Usage](#example-usage)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## Overview
This RESTful API, developed with **FastAPI** and **PostgreSQL**, enables users to manage a ToDo list with secure **JWT authentication**. Key features include:

- **User Management**: Register users with first name, last name (optional), unique username, and password (min 6 characters).
- **Task Management**: Create, read, update, and delete tasks with title, description (optional), status (NEW, IN_PROGRESS, COMPLETED), and user ownership.
- **Authentication & Authorization**: JWT-based authentication for protected endpoints; only task owners can modify their tasks.
- **Pagination & Filtering**: Paginated task retrieval with skip and limit parameters, plus optional status filtering.
- **Testing**: Comprehensive unit tests (~30 tests) for user and task endpoints using pytest, covering edge cases and validation.
- **Docker Support**: Dockerized setup with PostgreSQL.
- **Environment Configuration**: Managed via .env file for secure settings.
- **GitHub repository**: (https://github.com/sa6uhi/todo-api).

## Project Structure
Below is the project structure with descriptions of key files and directories, hyperlinked to its repository locations.

- **[app/](app/)**: Core application directory containing the FastAPI application code.
  - **[__init__.py](app/__init__.py)**: Initializes the app module.
  - **[auth.py](app/auth.py)**: Handles JWT authentication, token creation, and user verification.
  - **[crud.py](app/crud.py)**: Contains CRUD operations for users and tasks using SQLAlchemy.
  - **[database.py](app/database.py)**: Configures the PostgreSQL database connection and SQLAlchemy setup.
  - **[deps.py](app/deps.py)**: Defines dependency injection for database sessions.
  - **[main.py](app/main.py)**: Main FastAPI application with endpoint definitions.
  - **[models.py](app/models.py)**: Defines SQLAlchemy models for User and Task with relationships.
  - **[schemas.py](app/schemas.py)**: Pydantic schemas for data validation and serialization.
- **[tests/](tests/)**: Directory for unit tests.
  - **[conftest.py](tests/conftest.py)**: Pytest fixtures for setting up test database and client.
  - **[test_tasks.py](tests/test_tasks.py)**: Unit tests for task-related endpoints.
  - **[test_users.py](tests/test_users.py)**: Unit tests for user-related endpoints.
- **[.dockerignore](.dockerignore)**: Excludes files from Docker builds.
- **[.env.example](.env.example)**: Template for environment variables configuration.
- **[.gitignore](.gitignore)**: Specifies files and directories to exclude from Git version control.
- **[docker-compose.yml](docker-compose.yml)**: Configures Docker services for the API and PostgreSQL database.
- **[Dockerfile](Dockerfile)**: Defines the Docker image for the FastAPI application.
- **[pytest.ini](pytest.ini)**: Configures pytest settings.
- **[requirements.txt](requirements.txt)**: Lists Python dependencies for the project.

## Installation

### Local Setup
To run the application locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sa6uhi/todo-api.git
   cd todo-api
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to set your environment variables (see [Environment Variables](#environment-variables) for details).

5. **Set Up PostgreSQL Database**:
   - Install PostgreSQL if not already installed (e.g., via `apt`, `brew`, or PostgreSQL installer).
   - Create a database named `todo_db`:
     ```bash
     psql -U postgres
     CREATE DATABASE todo_db;
     ```
   - Ensure the database credentials in `.env` match your PostgreSQL setup (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`).

6. **Run the Application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`. Access the interactive API docs at `http://localhost:8000/docs`.

### Docker Setup
To run the application using Docker, follow these steps for a seamless deployment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sa6uhi/todo-api.git
   cd todo-api
   ```

2. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` to set your environment variables (see [Environment Variables](#environment-variables) for detailed instructions).
   - For Docker, ensure `POSTGRES_HOST` is set to `db` (the service name in `docker-compose.yml`) to allow the API to connect to the PostgreSQL container.

3. **Build and Run with Docker Compose**:
   - Build the Docker images and start the services:
     ```bash
     docker-compose up --build
     ```
   - This command builds the FastAPI application image and starts both the API(`api`) and PostgreSQL(`db`) containers. The `wait-for-it.sh` script ensures the API waits for the database to be ready before starting.
   - The API will be available at `http://localhost:8000`. The PostgreSQL database runs in a separate container (`db`) and persists data in a Docker volume (`postgres_data`).

4. **Access the Application**:
   - Open `http://localhost:8000/docs` for interactive API documentation (powered by FastAPI's Swagger UI).
   - Use `http://localhost:8000/redoc` for alternative API documentation.
   - To connect to the database manually, use a PostgreSQL client (e.g., `psql` or pgAdmin) with the credentials from `.env` (host: `localhost`, port: `5432` when running locally, or connect to the `db` container).

5. **Monitor Containers**:
   - Check running containers:
     ```bash
     docker-compose ps
     ```
   - View logs for debugging:
     ```bash
     docker-compose logs api
     docker-compose logs db
     ```

6. **Stop and Clean Up**:
   - Stop the containers:
     ```bash
     docker-compose down
     ```
   - To remove volumes (including database data):
     ```bash
     docker-compose down -v
     ```

7. **Troubleshooting**:
   - If the API fails to start, ensure the `.env` file is correctly configured, especially `SECRET_KEY` and `POSTGRES_HOST=db`.
   - Check PostgreSQL health with:
     ```bash
     docker-compose exec db pg_isready -U todo_user -d todo_db
     ```
   - If port `8000` is in use, modify `docker-compose.yml` to map a different host port (e.g., `8001:8000`).

## Running Tests

### Local Environment
To run unit tests locally, ensure the virtual environment is activated and dependencies are installed.

1. **Run Tests**:
   ```bash
   pytest tests/ -v
   ```
   Executes ~30 tests in `tests/` using an in-memory SQLite database for isolation, covering user/task endpoints, validation, and edge cases. The `-v` flag provides verbose output.

### Docker Environment
To run tests in a Docker container, ensure the Docker services are running.

1. **Build the Docker Image**:
   ```bash
   docker-compose build
   ```

2. **Run Tests**:
   ```bash
   docker-compose exec api pytest -v tests/
   ```
   This runs the tests inside the `api` container using the in-memory SQLite database defined in `tests/conftest.py`. The `-v` flag provides verbose output. Note that `tests/` is the correct path within the container, as the project is mounted at `/app`.

## API Endpoints
All endpoints are documented in the interactive Swagger UI at `http://localhost:8000/docs`. Below is a detailed description of each endpoint, including request/response formats, headers, and possible errors.

### Authentication
- **POST /token**
  - **Description**: Authenticates a user and returns a JWT access token for accessing protected endpoints.
  - **Request**:
    - Method: POST
    - Content-Type: `application/x-www-form-urlencoded`
    - Body: `username=<string>&password=<string>`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "access_token": "<jwt-token>", "token_type": "bearer" }`
    - Example: `{ "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer" }`
  - **Errors**:
    - 401 Unauthorized: `{ "detail": "Incorrect username or password!" }` if credentials are invalid.
  - **Notes**: The token expires after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in [auth.py](app/auth.py)).

### User Endpoints
- **POST /users/**
  - **Description**: Creates a new user with a unique username and hashed password.
  - **Request**:
    - Method: POST
    - Content-Type: `application/json`
    - Body: `{ "first_name": "<string>", "last_name": "<string|null>", "username": "<string>", "password": "<string>" }`
    - Example: `{ "first_name": "Sabuhi", "last_name": "Nazarov", "username": "sa6uhi", "password": "sabuhi123" }`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "id": <int>, "first_name": "<string>", "last_name": "<string|null>", "username": "<string>" }`
    - Example: `{ "id": 1, "first_name": "Sabuhi", "last_name": "Nazarov", "username": "sa6uhi" }`
  - **Errors**:
    - 400 Bad Request: `{ "detail": "Username already registered!" }` if username exists.
    - 422 Unprocessable Entity: If `first_name` or `username` is empty, or `password` is less than 6 characters.
  - **Notes**: Passwords are hashed using bcrypt before storage ([auth.py](app/auth.py)).

- **DELETE /users/me**
  - **Description**: Deletes the authenticated user's account and all associated tasks.
  - **Request**:
    - Method: DELETE
    - Headers: `Authorization: Bearer <jwt-token>`
    - Example: `/users/me`
  - **Response**:
    - Status: 200 OK
    - Body: None
  - **Errors**:
    - 401 Unauthorized: `{ "detail": "Not authenticated" }` if no token is provided.
    - 401 Unauthorized: `{ "detail": "Couldn't validate credentials!" }` if token is invalid or missing user ID.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 404 Not Found: `{ "detail": "User not found!" }` if the user does not exist in the database.
  - **Notes**: 
    - Deletes the authenticated user’s account using the user ID from the JWT token.
    - All associated tasks are deleted due to cascading deletion.

### Task Endpoints
- **POST /tasks/**
  - **Description**: Creates a new task for the authenticated user.
  - **Request**:
    - Method: POST
    - Content-Type: `application/json`
    - Headers: `Authorization: Bearer <jwt-token>`
    - Body: `{ "title": "<string>", "description": "<string|null>", "status": "NEW|IN_PROGRESS|COMPLETED" }`
    - Example: `{ "title": "Finish project", "description": "Complete API", "status": "NEW" }`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "id": <int>, "title": "<string>", "description": "<string|null>", "status": "<string>", "user_id": <int> }`
    - Example: `{ "id": 1, "title": "Finish project", "description": "Complete API", "status": "NEW", "user_id": 1 }`
  - **Errors**:
    - 401 Unauthorized: `{ "detail": "Not authenticated" }` if no token is provided.
    - 401 Unauthorized: `{ "detail": "Couldn't validate credentials!" }` if token is invalid.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 422 Unprocessable Entity: If `title` is empty or exceeds 100 characters, or `description` exceeds 500 characters.
  - **Notes**: 
    - The task is automatically associated with the authenticated user. 
    - The `status` field must be one of `NEW`, `IN_PROGRESS`, or `COMPLETED` in uppercase. Lowercase or mixed-case values (e.g., `new`, `In_Progress`) will result in a 422 Unprocessable Entity error.

- **GET /tasks/**
  - **Description**: Retrieves a paginated list of all tasks, optionally filtered by status.
  - **Request**:
    - Method: GET
    - Query Parameters:
      - `skip`: Integer, default 0, for pagination offset.
      - `limit`: Integer, default 10, for page size.
      - `status`: Optional, one of `NEW`, `IN_PROGRESS`, `COMPLETED`.
    - Example: `/tasks/?skip=0&limit=10&status=NEW`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "items": [{ "id": <int>, "title": "<string>", "description": "<string|null>", "status": "<string>", "user_id": <int> }], "total": <int>, "skip": <int>, "limit": <int> }`
    - Example: `{ "items": [{ "id": 1, "title": "Finish project", "description": "Complete API", "status": "NEW", "user_id": 1 }], "total": 1, "skip": 0, "limit": 10 }`
  - **Errors**:
    - 400 Bad Request: `{ "detail": "Skip must be non-negative!" }` if `skip` < 0.
    - 400 Bad Request: `{ "detail": "Limit must be between 1 and 100 (inclusive)!" }` if `limit` ≤ 0 or `limit` ≥ 100.
    - 400 Bad Request: `{ "detail": "Skip value {skip} exceeds total tasks {total}" }` if `skip` is greater than or equal to the total number of tasks.
  - **Notes**: No authentication is required for this endpoint.

- **GET /tasks/user/**
  - **Description**: Retrieves a paginated list of tasks for the authenticated user.
  - **Request**:
    - Method: GET
    - Headers: `Authorization: Bearer <jwt-token>`
    - Query Parameters:
      - `skip`: Integer, default 0, for pagination offset.
      - `limit`: Integer, default 10, for page size.
    - Example: `/tasks/user/?skip=0&limit=10`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "items": [{ "id": <int>, "title": "<string>", "description": "<string|null>", "status": "<string>", "user_id": <int> }], "total": <int>, "skip": <int>, "limit": <int> }`
  - **Errors**:
    - 401 Unauthorized: If no valid token is provided.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 400 Bad Request: `{ "detail": "Skip must be non-negative!" }` if `skip` < 0.
    - 400 Bad Request: `{ "detail": "Limit must be between 1 and 100 (inclusive)!" }` if `limit` ≤ 0 or `limit` ≥ 100.
    - 400 Bad Request: `{ "detail": "Skip value {skip} exceeds total user tasks {total}" }` if `skip` is greater than or equal to the total number of user tasks.
  - **Notes**: Only returns tasks owned by the authenticated user.

- **GET /tasks/{task_id}**
  - **Description**: Retrieves details of a specific task by ID.
  - **Request**:
    - Method: GET
    - Path Parameter: `task_id` (integer)
    - Example: `/tasks/1`
  - **Response**:
    - Status: 200 OK
    - Body: `{ "id": <int>, "title": "<string>", "description": "<string|null>", "status": "<string>", "user_id": <int> }`
  - **Errors**:
    - 404 Not Found: `{ "detail": "Task not found!" }` if task ID does not exist.
  - **Notes**: No authentication is required.

- **PUT /tasks/{task_id}**
  - **Description**: Updates a task (only by the task owner).
  - **Request**:
    - Method: PUT
    - Path Parameter: `task_id` (integer)
    - Headers: `Authorization: Bearer <jwt-token>`
    - Body: `{ "title": "<string>", "description": "<string|null>", "status": "NEW|IN_PROGRESS|COMPLETED" }`
    - Example: `/tasks/1` with body `{ "title": "Updated project", "description": "Updated API", "status": "IN_PROGRESS" }`
  - **Response**:
    - Status: 200 OK
    - Body: Updated task object
  - **Errors**:
    - 401 Unauthorized: If no valid token is provided.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 403 Forbidden: `{ "detail": "Not authorized to update this task!" }` if user is not the task owner.
    - 404 Not Found: If task ID does not exist.
    - 422 Unprocessable Entity: If input validation fails.
  - **Notes**: 
    - Partial updates are supported (unchanged fields retain their values).
    - The `status` field must be one of `NEW`, `IN_PROGRESS`, or `COMPLETED` in uppercase. Lowercase or mixed-case values (e.g., `new`, `In_Progress`) will result in a 422 Unprocessable Entity error.
    - An empty payload (`{}`) is valid and returns the unchanged task.
    - Title must be between 1 and 100 characters; description cannot exceed 500 characters.

- **PATCH /tasks/{task_id}/complete**
  - **Description**: Marks a task as COMPLETED (only by the task owner).
  - **Request**:
    - Method: PATCH
    - Path Parameter: `task_id` (integer)
    - Headers: `Authorization: Bearer <jwt-token>`
    - Example: `/tasks/1/complete`
  - **Response**:
    - Status: 200 OK
    - Body: Updated task object with `status: "COMPLETED"`
  - **Errors**:
    - 400 Bad Request: `{ "detail": "Task is already completed!" }` if the task is already in COMPLETED status.
    - 401 Unauthorized: If no valid token is provided.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 403 Forbidden: If user is not the task owner.
    - 404 Not Found: If task ID does not exist.
  - **Notes**: Only changes the `status` field to `COMPLETED`.

- **DELETE /tasks/{task_id}**
  - **Description**: Deletes a task (only by the task owner).
  - **Request**:
    - Method: DELETE
    - Path Parameter: `task_id` (integer)
    - Headers: `Authorization: Bearer <jwt-token>`
    - Example: `/tasks/1`
  - **Response**:
    - Status: 200 OK
    - Body: None
  - **Errors**:
    - 401 Unauthorized: If no valid token is provided.
    - 401 Unauthorized: `{ "detail": "Token has expired!" }` if the JWT token is expired.
    - 403 Forbidden: If user is not the task owner.
    - 404 Not Found: If task ID does not exist.
  - **Notes**: Deletes the task permanently from the database.

### Example Usage
Below are example API calls using `curl`. Replace `<token>` with a valid JWT obtained from `/token`.

1. **Create a User**:
   ```bash
   curl -X POST "http://localhost:8000/users/" \
   -H "Content-Type: application/json" \
   -d '{"first_name":"Sabuhi","last_name":"Nazarov","username":"sa6uhi","password":"sabuhi123"}'
   ```

2. **Obtain a Token**:
   ```bash
   curl -X POST "http://localhost:8000/token" \
   -H "Content-Type: application/x-www-form-urlencoded" \
   -d "username=sa6uhi&password=sabuhi123"
   ```

3. **Create a Task**:
   ```bash
   curl -X POST "http://localhost:8000/tasks/" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer <token>" \
   -d '{"title":"Finish project","description":"Complete the ToDo API","status":"NEW"}'
   ```

4. **Get Paginated Tasks with Status Filter**:
   ```bash
   curl -X GET "http://localhost:8000/tasks/?skip=0&limit=10&status=NEW"
   ```

5. **Get User Tasks**:
   ```bash
   curl -X GET "http://localhost:8000/tasks/user/?skip=0&limit=10" \
   -H "Authorization: Bearer <token>"
   ```

6. **Get Task by ID**:
   ```bash
   curl -X GET "http://localhost:8000/tasks/1"
   ```

7. **Update a Task**:
   ```bash
   curl -X PUT "http://localhost:8000/tasks/1" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer <token>" \
   -d '{"title":"Updated project","description":"Updated description","status":"IN_PROGRESS"}'
   ```

8. **Mark a Task as Completed**:
   ```bash
   curl -X PATCH "http://localhost:8000/tasks/1/complete" \
   -H "Authorization: Bearer <token>"
   ```

9. **Delete a Task**:
   ```bash
   curl -X DELETE "http://localhost:8000/tasks/1" \
   -H "Authorization: Bearer <token>"
   ```

10. **Delete a User**:
   ```bash
   curl -X DELETE "http://localhost:8000/users/me" \
   -H "Authorization: Bearer <token>"

## Environment Variables
The application uses a `.env` file to manage configuration securely. Copy `.env.example` to `.env` and update the values as described below:

1. **Create the `.env` File**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with the Following Variables**:
   - `POSTGRES_USER`: PostgreSQL username for database access.
     - Example: `todo_user`
     - Ensure this matches the user created in your PostgreSQL setup.
   - `POSTGRES_PASSWORD`: Password for the PostgreSQL user.
     - Example: `todo_password`
     - Use a secure password, avoiding special characters that may cause parsing issues.
   - `POSTGRES_HOST`: Database host.
     - Use `localhost` for local development.
     - Use `db` (the service name in `docker-compose.yml`) for Docker.
   - `POSTGRES_PORT`: Database port.
     - Default: `5432`
     - Ensure this matches your PostgreSQL configuration.
   - `POSTGRES_DB`: Database name.
     - Example: `todo_db`
     - Must match the database created in PostgreSQL.
   - `SECRET_KEY`: Secret key for JWT token signing.
     - Generate a secure key using:
       ```bash
       openssl rand -hex 32
       ```
     - Example: `your-secure-secret-key-1234567890abcdef`
     - Keep this secret and unique for each deployment.
   - `JWT_ALGORITHM`: Algorithm for JWT encoding.
     - Default: `HS256`
     - Example: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes.
     - Default: `30`
     - Example: `30`

3. **Example `.env`**:
   ```
   POSTGRES_USER=todo_user
   POSTGRES_PASSWORD=todo_password
   POSTGRES_HOST=localhost  # Use 'db' for Docker
   POSTGRES_PORT=5432
   POSTGRES_DB=todo_db
   SECRET_KEY=your-secure-secret-key-1234567890abcdef
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Security Notes**:
   - Never commit the `.env` file to version control (it’s excluded in [.gitignore](.gitignore)).
   - Ensure `SECRET_KEY` is unique and not shared publicly.
   - For production, consider using a secrets management tool (e.g., AWS Secrets Manager, HashiCorp Vault).

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository (https://github.com/sa6uhi/todo-api).
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.