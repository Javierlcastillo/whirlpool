# Generated by Django 4.2.7 on 2025-03-13 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number', models.PositiveIntegerField(default=1, verbose_name='Número')),
                ('answer', models.TextField(verbose_name='Texto de la respuesta')),
                ('media', models.FileField(blank=True, null=True, upload_to='answers/', verbose_name='Medio (imagen, video)')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Es correcta')),
            ],
            options={
                'verbose_name': 'Respuesta',
                'verbose_name_plural': 'Respuestas',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('duration_weeks', models.PositiveSmallIntegerField(verbose_name='Duración (semanas)')),
                ('category', models.CharField(choices=[('reparacion', 'Reparación'), ('instalacion', 'Instalación'), ('diagnostico', 'Diagnóstico'), ('mantenimiento', 'Mantenimiento')], default='reparacion', max_length=20, verbose_name='Categoría')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última actualización')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CourseApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Aplicación de Curso',
                'verbose_name_plural': 'Aplicaciones de Cursos',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Región',
                'verbose_name_plural': 'Regiones',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Título')),
                ('text', models.TextField(blank=True, verbose_name='Texto')),
                ('image', models.ImageField(blank=True, null=True, upload_to='sections/', verbose_name='Imagen')),
                ('video_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='URL de video')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='courses.course', verbose_name='Curso')),
            ],
            options={
                'verbose_name': 'Sección',
                'verbose_name_plural': 'Secciones',
                'ordering': ['course', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number', models.PositiveIntegerField(default=1, verbose_name='Número')),
                ('text', models.TextField(verbose_name='Texto de la pregunta')),
                ('media', models.FileField(blank=True, null=True, upload_to='questions/', verbose_name='Medio (imagen, video)')),
                ('type', models.CharField(choices=[('multiple', 'Opción Múltiple'), ('open', 'Respuesta Abierta'), ('true_false', 'Verdadero/Falso')], default='multiple', max_length=20, verbose_name='Tipo')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='courses.course', verbose_name='Curso')),
            ],
            options={
                'verbose_name': 'Pregunta',
                'verbose_name_plural': 'Preguntas',
                'ordering': ['course', 'number'],
            },
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instructors', to='courses.region', verbose_name='Región')),
            ],
            options={
                'verbose_name': 'Instructor',
                'verbose_name_plural': 'Instructores',
            },
        ),
        migrations.CreateModel(
            name='Desempeno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('puntuacion', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Puntuación')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha')),
                ('estado', models.CharField(choices=[('started', 'Iniciado'), ('in_progress', 'En Progreso'), ('completed', 'Completado'), ('failed', 'Reprobado')], default='started', max_length=20, verbose_name='Estado')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='desempenos', to='courses.course', verbose_name='Curso')),
            ],
            options={
                'verbose_name': 'Desempeño',
                'verbose_name_plural': 'Desempeños',
            },
        ),
    ]
