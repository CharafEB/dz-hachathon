# College Timetable Generator

An intelligent, constraint-based academic scheduling solution powered by FastAPI and SQLAlchemy.

## Overview

The **College Timetable Generator** is a robust backend engine designed to automate the complex process of creating university schedules. It leverages a randomized greedy algorithm to assign sessions (lectures, tutorials, labs) to appropriate rooms and timeslots while strictly adhering to hard constraints such as teacher availability, room capacity, and group schedules.

## Key Features

-   **Automated Scheduling**: Constraint-based engine that minimizes conflicts and optimizes resource utilization.
-   **RESTful API**: Fully-featured API for managing all academic entities (Buildings, Rooms, Teachers, Departments, Courses, etc.).
-   **Security**: JWT-based authentication and role-based access control.
-   **Data Flexibility**: Support for importing initial data from JSON and persistence via SQLite/SQLAlchemy.
-   **Export Capabilities**: Support for generating structured reports and schedules.

## Tech Stack

-   **Backend**: Python 3.x, FastAPI
-   **Database**: SQLite with SQLAlchemy ORM
-   **Validation**: Pydantic
-   **Authentication**: Python-Jose (JWT), Passlib (Bcrypt)
-   **Export**: Python-docx

## Project Structure

```text
src/
├── api/                # FastAPI routes and app initialization
├── models.py           # SQLAlchemy database models
├── schemas.py          # Pydantic data schemas
├── scheduler.py        # Core scheduling logic
├── database.py         # Database connection and session management
├── auth.py             # Authentication and security utilities
└── migrate_json_to_db.py # Data migration script
```

## Getting Started

### Prerequisites

-   Python 3.8+
-   `pip` and `virtualenv`

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/CharafEB/College-timeable.git
    cd College-Timetable-Generator
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r src/requirements.txt
    ```

4.  **Initialize the database (Optional)**:
    If you have initial data in `data.json`, you can migrate it:
    ```bash
    cd src
    python migrate_json_to_db.py
    ```

### Running the Application

To start the development server, run the following command from the `src` directory:

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Usage

### Generating a Timetable

To trigger the scheduling engine, you can use the following API endpoint:

-   **Endpoint**: `GET /timetable?regenerate=true`
-   **Description**: Clears existing assignments and runs the scheduler to generate a new timetable based on current constraints.

### Authentication

Most management endpoints require a valid JWT token. For detailed information on how to authenticate, manage roles, and use the security features, please refer to the [Authentication Documentation](doc/AUTH.md).

You can obtain a token by signing up and logging in via the `/auth/signup` and `/auth/login` endpoints.

## License

This project is licensed under the MIT License.
