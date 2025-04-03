# Whirlpool Courses

A Django-based e-learning platform for managing and delivering courses.

## Features

- Course management (create, edit, delete)
- User authentication and authorization
- Course enrollment and progress tracking
- Question and answer system
- Section-based course content
- API endpoints for integration
- Docker support for easy deployment

## Requirements

- Python 3.9+
- PostgreSQL 13+
- Docker and Docker Compose (optional)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whirlpool.git
cd whirlpool
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

### Docker Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whirlpool.git
cd whirlpool
```

2. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

## API Documentation

The API is available at `/api/` and includes endpoints for:

- Courses
- Regions
- Instructors
- Questions
- Answers
- Sections
- Course Applications
- Enrollments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 