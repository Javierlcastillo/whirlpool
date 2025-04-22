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

La API está disponible en `/api/` e incluye endpoints para:

- Courses
- Regions
- Instructors
- Questions
- Answers
- Sections
- Course Applications
- Enrollments

La API ahora está integrada directamente en la aplicación `courses`, lo que simplifica la arquitectura y reduce la duplicación de código.

## API para Unity Game

Se ha implementado una API específica para facilitar la integración con un juego en Unity, proporcionando endpoints simplificados y optimizados para este propósito.

### Base URL

```
/api/unity/
```

### Autenticación

La autenticación se realiza mediante token. Para obtener un token, se debe hacer una petición POST al endpoint:

```
POST /api/token/
```

Con el siguiente cuerpo JSON:

```json
{
  "username": "numero_empleado",
  "password": "contraseña"
}
```

La respuesta incluirá un token que debe ser incluido en todas las peticiones subsiguientes en la cabecera HTTP:

```
Authorization: Token <tu_token>
```

### Endpoints disponibles

#### Información del usuario

```
GET /api/unity/user_info/
```

Devuelve información sobre el técnico autenticado:

```json
{
  "id": 1,
  "employee_number": "T12345",
  "name": "Nombre del Técnico",
  "region": "Norte",
  "is_active": true
}
```

#### Cursos disponibles

```
GET /api/unity/available_courses/
```

Devuelve la lista de cursos disponibles para el técnico según su región:

```json
[
  {
    "id": 1,
    "name": "Nombre del Curso",
    "slug": "nombre-del-curso",
    "description": "Descripción del curso",
    "instructor_name": "Nombre del Instructor",
    "duration_hours": 8
  }
]
```

#### Detalles de un curso

```
GET /api/unity/<slug_del_curso>/
```

Devuelve información detallada de un curso, incluyendo secciones y preguntas:

```json
{
  "id": 1,
  "name": "Nombre del Curso",
  "slug": "nombre-del-curso",
  "description": "Descripción del curso",
  "instructor_name": "Nombre del Instructor",
  "duration_hours": 8,
  "sections": [
    {
      "id": 1,
      "title": "Título de la Sección",
      "content": "Contenido de la sección...",
      "media": "URL_del_archivo_multimedia",
      "order": 1
    }
  ],
  "questions": [
    {
      "id": 1,
      "text": "¿Pregunta?",
      "type": "multiple_choice",
      "order": 1,
      "answers": [
        {
          "id": 1,
          "number": 1,
          "answer": "Respuesta 1",
          "is_correct": true
        },
        {
          "id": 2,
          "number": 2,
          "answer": "Respuesta 2",
          "is_correct": false
        }
      ]
    }
  ],
  "content_items": [
    {
      "type": "section",
      "id": 1,
      "title": "Título de la Sección",
      "content": "Contenido de la sección...",
      "media": "URL_del_archivo_multimedia",
      "order": 1
    },
    {
      "type": "question",
      "id": 1,
      "text": "¿Pregunta?",
      "type": "multiple_choice",
      "order": 2,
      "answers": [
        {
          "id": 1,
          "answer": "Respuesta 1",
          "is_correct": true,
          "number": 1
        },
        {
          "id": 2,
          "answer": "Respuesta 2",
          "is_correct": false,
          "number": 2
        }
      ]
    }
  ]
}
```

#### Enviar progreso

```
POST /api/unity/<slug_del_curso>/submit_progress/
```

Cuerpo de la petición:

```json
{
  "score": 85.5,
  "status": "completed"  // Valores posibles: "started", "in_progress", "completed", "failed"
}
```

Respuesta:

```json
{
  "success": true,
  "message": "Progreso registrado correctamente",
  "desempeno_id": 1
}
```

### Integración con Unity

Para utilizar esta API desde Unity, se recomienda:

1. Utilizar UnityWebRequest para las peticiones HTTP
2. Almacenar el token de autenticación en PlayerPrefs después del login
3. Incluir el token en todas las peticiones subsiguientes
4. Usar Newtonsoft.Json para deserializar las respuestas

Ejemplo de código en C#:

```csharp
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class ApiManager : MonoBehaviour
{
    private const string API_BASE_URL = "https://tu-dominio.com/api/";
    private const string TOKEN_KEY = "auth_token";
    
    public IEnumerator Login(string username, string password)
    {
        string url = API_BASE_URL + "token/";
        string jsonData = JsonConvert.SerializeObject(new { username, password });
        
        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonData))
        {
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<TokenResponse>(request.downloadHandler.text);
                PlayerPrefs.SetString(TOKEN_KEY, response.token);
                PlayerPrefs.Save();
            }
            else
            {
                Debug.LogError("Error: " + request.error);
            }
        }
    }
    
    public IEnumerator GetAvailableCourses()
    {
        string url = API_BASE_URL + "unity/available_courses/";
        string token = PlayerPrefs.GetString(TOKEN_KEY);
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", "Token " + token);
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var courses = JsonConvert.DeserializeObject<List<Course>>(request.downloadHandler.text);
                // Procesar los cursos...
            }
            else
            {
                Debug.LogError("Error: " + request.error);
            }
        }
    }
}

// Clases para deserialización
[System.Serializable]
public class TokenResponse
{
    public string token;
}

[System.Serializable]
public class Course
{
    public int id;
    public string name;
    public string slug;
    public string description;
    public string instructor_name;
    public int duration_hours;
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 