"""
Script para inicializar datos de ejemplo en la aplicación.
Ejecutar con: python manage.py shell < initialize_data.py
"""

from django.contrib.auth.models import User
from users.models import Technician
from courses.models import Course, Question, Answer, FAQ
from django.utils.text import slugify

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@whirlpool.com',
        password='admin',
        first_name='Admin',
        last_name='Whirlpool'
    )
    print("Superusuario creado: admin / admin")
else:
    admin_user = User.objects.get(username='admin')

# Crear algunos técnicos
tech_data = [
    {
        'username': 'juan',
        'password': 'password',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'email': 'juan@whirlpool.com',
        'employee_number': '123',
        'region': 'norte'
    },
    {
        'username': 'ana',
        'password': 'password',
        'first_name': 'Ana',
        'last_name': 'López',
        'email': 'ana@whirlpool.com',
        'employee_number': '234',
        'region': 'sur'
    },
    {
        'username': 'carlos',
        'password': 'password',
        'first_name': 'Carlos',
        'last_name': 'Martínez',
        'email': 'carlos@whirlpool.com',
        'employee_number': '345',
        'region': 'centro'
    }
]

technicians = []
for tech in tech_data:
    if not User.objects.filter(username=tech['username']).exists():
        user = User.objects.create_user(
            username=tech['username'],
            password=tech['password'],
            first_name=tech['first_name'],
            last_name=tech['last_name'],
            email=tech['email']
        )
        technician = Technician.objects.create(
            user=user,
            employee_number=tech['employee_number'],
            region=tech['region']
        )
        technicians.append(technician)
        print(f"Técnico creado: {tech['first_name']} {tech['last_name']}")
    else:
        user = User.objects.get(username=tech['username'])
        technician, created = Technician.objects.get_or_create(
            user=user,
            defaults={
                'employee_number': tech['employee_number'],
                'region': tech['region']
            }
        )
        technicians.append(technician)
        if created:
            print(f"Técnico creado: {tech['first_name']} {tech['last_name']}")

# Crear algunos cursos
course_data = [
    {
        'title': 'Reparación de Lavadoras',
        'description': 'Curso completo para la reparación de lavadoras Whirlpool, incluyendo diagnóstico y solución de problemas comunes.',
        'instructor': technicians[0],
        'duration_weeks': 4,
        'category': 'reparacion'
    },
    {
        'title': 'Instalación de Secadoras',
        'description': 'Aprende las mejores prácticas para la instalación de secadoras Whirlpool, incluyendo conexiones eléctricas y de ventilación.',
        'instructor': technicians[1],
        'duration_weeks': 3,
        'category': 'instalacion'
    },
    {
        'title': 'Diagnóstico de Refrigeradores',
        'description': 'Curso avanzado para el diagnóstico y solución de problemas en refrigeradores Whirlpool.',
        'instructor': technicians[2],
        'duration_weeks': 5,
        'category': 'diagnostico'
    }
]

courses = []
for course_info in course_data:
    title = course_info['title']
    slug = slugify(title)
    
    course, created = Course.objects.get_or_create(
        title=title,
        defaults={
            'slug': slug,
            'description': course_info['description'],
            'instructor': course_info['instructor'],
            'duration_weeks': course_info['duration_weeks'],
            'category': course_info['category']
        }
    )
    courses.append(course)
    if created:
        print(f"Curso creado: {title}")

# Crear algunas preguntas y respuestas
question_data = [
    {
        'course': courses[0],
        'text': '¿Cuál es el primer paso al diagnosticar una lavadora que no enciende?',
        'answers': [
            {'text': 'Verificar la conexión eléctrica', 'is_correct': True},
            {'text': 'Revisar el tambor', 'is_correct': False},
            {'text': 'Cambiar el motor', 'is_correct': False}
        ]
    },
    {
        'course': courses[0],
        'text': '¿Qué herramienta es esencial para medir la continuidad en componentes eléctricos?',
        'answers': [
            {'text': 'Destornillador', 'is_correct': False},
            {'text': 'Multímetro', 'is_correct': True},
            {'text': 'Llave inglesa', 'is_correct': False}
        ]
    },
    {
        'course': courses[1],
        'text': '¿Cuál es la distancia mínima recomendada entre una secadora y la pared?',
        'answers': [
            {'text': '5 cm', 'is_correct': False},
            {'text': '10 cm', 'is_correct': True},
            {'text': '15 cm', 'is_correct': False}
        ]
    }
]

for i, q_data in enumerate(question_data):
    question, created = Question.objects.get_or_create(
        course=q_data['course'],
        text=q_data['text'],
        defaults={'order': i + 1}
    )
    
    if created:
        print(f"Pregunta creada: {q_data['text'][:30]}...")
        
        # Crear respuestas
        for j, a_data in enumerate(q_data['answers']):
            answer = Answer.objects.create(
                question=question,
                text=a_data['text'],
                is_correct=a_data['is_correct']
            )
            print(f"  Respuesta creada: {a_data['text']}")

# Crear algunas FAQs
faq_data = [
    {
        'question': '¿Cuál es la diferencia entre HTML y CSS?',
        'answer': 'HTML le da estructura a la página y mientras que CSS le da estilo o apariencia a la página.'
    },
    {
        'question': '¿Qué es una propiedad CSS y cómo se utiliza?',
        'answer': 'Una propiedad CSS es un atributo que controla un aspecto específico del estilo de un elemento HTML. Por ejemplo, text-align sirve para alinear el texto dependiendo en donde se especifique.'
    },
    {
        'question': '¿Cómo se utiliza la propiedad background-color para cambiar el color de fondo?',
        'answer': 'Esta función sirve para cambiar todo el fondo del componente a un color sólido. Se especifica con valores hexadecimales, RGB o nombres de colores.'
    },
    {
        'question': '¿Qué es y cómo se crea un layout en CSS?',
        'answer': 'Es una estructura que define cómo se visualizan los elementos. Existen varias maneras de crear una, por ejemplo usando Flexbox, Grid o frameworks como Bootstrap.'
    },
    {
        'question': '¿Nombre alguna herramienta que te genere plantillas o código con CSS?',
        'answer': 'Existen varias como: Bootstrap, Tailwind CSS, Foundation, Bulma, entre otras.'
    }
]

for i, faq_info in enumerate(faq_data):
    faq, created = FAQ.objects.get_or_create(
        question=faq_info['question'],
        defaults={
            'answer': faq_info['answer'],
            'order': i + 1
        }
    )
    if created:
        print(f"FAQ creada: {faq_info['question'][:30]}...")

print("\nInicialización de datos completada exitosamente!")
print("Ahora puedes acceder al sistema con los siguientes usuarios:")
print("  Admin: admin / admin")
print("  Técnico: juan / password")
print("  Técnico: ana / password")
print("  Técnico: carlos / password")