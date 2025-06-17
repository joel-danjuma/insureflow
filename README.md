# InsureFlow API

InsureFlow is a comprehensive, modern insurance management platform designed to handle policies, premiums, payments, and user management with a role-based access control system. The application is built with a FastAPI backend, a PostgreSQL database, and a Streamlit dashboard for payment monitoring.

## Major Features

- **Robust Backend**: Built with FastAPI, offering high performance and automatic interactive API documentation.
- **Database Management**: Uses PostgreSQL with SQLAlchemy for the ORM and Alembic for handling database migrations.
- **Multi-Tenant Authentication**: Secure JWT-based authentication system with role-based access control for Admins, Brokers, and Customers.
- **Payment Processing**: End-to-end payment flow integrated with the Squad Co payment gateway, including payment initiation and webhook handling for payment confirmations.
- **User Management**: Complete CRUD API for managing users, with role-based authorization to protect sensitive operations.
- **Policy & Premium Management**: RESTful APIs for creating, retrieving, updating, and deleting insurance policies and their associated premiums.
- **Dockerized Environment**: Fully containerized development environment using Docker and Docker Compose for easy setup and consistency across machines.
- **Payment Monitoring Dashboard**: A basic Streamlit dashboard to monitor payments and their statuses in real-time.
- **Asynchronous Caching**: Integrated Redis for caching frequently accessed data, such as user profiles, to improve performance.

## API Documentation

The InsureFlow API is self-documenting thanks to FastAPI. Once the application is running, you can access the interactive API documentation at the following endpoints:

- **Swagger UI**: [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs)
- **ReDoc**: [`http://localhost:8000/api/v1/redoc`](http://localhost:8000/api/v1/redoc)

These interfaces provide detailed information about all available endpoints, their parameters, and response models. You can also use them to interact with the API directly from your browser.

## Setup and Installation

To get the InsureFlow application running locally, you will need to have Docker and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd insureflow
    ```

2.  **Create the environment file:**
    Copy the `env.example` file to a new file named `app.env`.
    ```bash
    cp env.example app.env
    ```
    Review the `app.env` file and fill in any necessary values, such as your Squad Co API keys.

3.  **Build and run the application:**
    Use Docker Compose to build and run all the services in the background.
    ```bash
    docker-compose up --build -d
    ```
    This command will build the Docker images for the FastAPI application and the Streamlit dashboard, and start all the necessary services, including the PostgreSQL database and Redis cache.

## Interacting with the Application

Once the services are running, you can interact with them as follows:

- **FastAPI Backend**: The main application is available at [`http://localhost:8000`](http://localhost:8000).
- **Streamlit Dashboard**: The payment monitoring dashboard is available at [`http://localhost:8501`](http://localhost:8501).

You can use an API client like Postman or Insomnia to interact with the API endpoints, or use the interactive documentation linked above. 