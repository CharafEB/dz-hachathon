# Authentication Documentation

This document describes the authentication system used in the College Timetable Generator.

## Overview

The system uses **JWT (JSON Web Tokens)** for stateless authentication. Security is implemented using FastAPI's dependency injection system, with roles to restrict access to management endpoints.

## Authentication Scheme

-   **Type**: Bearer Token (JWT)
-   **Header**: `Authorization: Bearer <your_token>`
-   **Algorithm**: HS256
-   **Default Expiration**: 24 hours (1440 minutes)

## Security Roles

| Role | Description |
| :--- | :--- |
| `admin` | Full access to all endpoints, including user management and system-wide settings. |
| `teacher` | Access to view schedules and manage assigned courses/sessions. |

---

## Endpoints

### 1. Register User
Create a new user account and log in automatically.

-   **Method**: `POST`
-   **URL**: `/auth/register`
-   **Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "strong_password",
      "role": "teacher"
    }
    ```
-   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "User registered and logged in successfully",
      "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
          "id": "uuid-string",
          "email": "user@example.com",
          "role": "teacher",
          "is_active": true
        }
      }
    }
    ```

### 2. Login
Authenticate and receive a JWT token.

-   **Method**: `POST`
-   **URL**: `/auth/login`
-   **Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "strong_password"
    }
    ```
-   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Login successful",
      "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
          "id": "uuid-string",
          "email": "user@example.com",
          "role": "teacher",
          "is_active": true
        }
      }
    }
    ```

### 3. Get Token Details
Retrieve the decoded payload of the provided JWT token.

-   **Method**: `GET`
-   **URL**: `/auth/me`
-   **Headers**: `Authorization: Bearer <token>`
-   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Token decoded successfully",
      "data": {
        "sub": "uuid-string",
        "role": "teacher",
        "exp": 1713214572
      }
    }
    ```

---

## Security Implementation Details

-   **Password Hashing**: Bcrypt using `passlib`.
-   **Token Verification**: `python-jose` library.
-   **Protected Routes**: Use the `get_current_user` dependency in FastAPI routes.
-   **Admin Only**: Use `require_admin` dependency for sensitive management routes.
