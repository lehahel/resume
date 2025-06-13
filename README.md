# FastAPI Backend (vibecoded in 3h)

A modern FastAPI backend application with basic setup and configuration.

## Setup

1. Create a virtual environment (if not already created):
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application, use the following command:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## Available Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `POST /register`: Register a new user
  - Request body:
    ```json
    {
        "Name": "string",
        "Email": "string",
        "Password": "string"
    }
    ```
  - Returns user information (excluding password)

## Database

The application uses SQLite as the database, which is automatically created when you first run the application. The database file will be created as `users.db` in the project root directory.

The database includes a `users` table with the following fields:
- id (Integer, Primary Key)
- name (String)
- email (String, Unique)
- password_hash (String) 
