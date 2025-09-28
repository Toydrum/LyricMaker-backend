# Syllable Division Application

This is a Django backend for a syllable division application that connects to an Angular frontend. The application is designed to provide an API for dividing words into syllables.

## Project Structure

```
syllable-division-backend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example
├── README.md
├── scripts/
│   └── entrypoint.sh
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       └── prod.py
├── apps/
│   └── syllables/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services/
│       │   └── syllable_divider.py
│       ├── migrations/
│       │   └── __init__.py
│       └── tests/
│           ├── __init__.py
│           └── test_api.py
├── common/
│   ├── __init__.py
│   └── utils.py
├── static/
│   └── .gitkeep
└── media/
    └── .gitkeep
```

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd syllable-division-backend
   ```

2. **Create a Virtual Environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```
   python manage.py migrate
   ```

5. **Start the Development Server**
   ```
   python manage.py runserver
   ```

## Docker Deployment

To deploy the application using Docker, follow these steps:

1. **Build the Docker Image**
   ```
   docker-compose build
   ```

2. **Run the Docker Container**
   ```
   docker-compose up
   ```

## Environment Variables

Create a `.env` file in the root directory based on the `.env.example` file to configure your environment variables.

## API Documentation

Refer to the API documentation for details on how to use the endpoints provided by the syllable division application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.