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

## Default Test Credentials

For testing and development purposes, you can create a test user with known credentials:

**Test User Credentials:**
- **Email**: `test@insureflow.com`
- **Password**: `TestPassword123!`
- **Role**: BROKER

### Creating the Test User

To create the test user, run the following command after the containers are running:

```bash
docker exec -it insureflow_app python scripts/create_test_user.py
```

This will create a broker user that you can use to login and test the application with real database data.

### Using the Test User

1. Navigate to your application's login page
2. Enter the email: `test@insureflow.com`
3. Enter the password: `TestPassword123!`
4. You should now be logged in and able to see real policies and premiums from the database

## Testing the Fixes

After deploying the authentication fixes, follow these steps to verify everything works:

1. **Restart the Docker containers** to apply backend changes:
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

2. **Create the test user**:
   ```bash
   docker exec -it insureflow_app python scripts/create_test_user.py
   ```

3. **Clear browser Session Storage**:
   - Open Developer Tools (F12)
   - Go to Application → Session Storage
   - Delete the `auth-storage` entry
   - Refresh the page

4. **Login with test credentials** via the UI

5. **Verify real data is displayed**:
   - Check that you see actual policies from the database (not mock data)
   - Verify payment status updates work correctly
   - Confirm all API calls are authenticated properly

### Expected Results

After the authentication fixes:
- ✅ Registration endpoint works properly
- ✅ Frontend displays real database data (87 policies, 671 premiums in your current database)
- ✅ Authentication uses real JWT tokens instead of "mock-token"
- ✅ Payment status updates reflect immediately on insurance firm dashboard
- ✅ No more mock data fallbacks 