# Generated by Django 4.2.7 on 2025-03-04 04:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_technician_created_at_technician_is_active'),
        ('courses', '0002_delete_faq'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['course', 'order'], 'verbose_name': 'Pregunta', 'verbose_name_plural': 'Preguntas'},
        ),
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, help_text='Explicación que se mostrará después de responder', null=True, verbose_name='Explicación'),
        ),
        migrations.AddField(
            model_name='question',
            name='title',
            field=models.CharField(blank=True, max_length=255, verbose_name='Título'),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
            name='TechnicianProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False, verbose_name='Completado')),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Calificación')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inicio')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de finalización')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='courses.course', verbose_name='Curso')),
                ('technician', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='users.technician', verbose_name='Técnico')),
            ],
            options={
                'verbose_name': 'Progreso del técnico',
                'verbose_name_plural': 'Progresos de los técnicos',
                'unique_together': {('technician', 'course')},
            },
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(verbose_name='Es correcta')),
                ('response_time', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de respuesta')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='courses.answer', verbose_name='Respuesta seleccionada')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='courses.question', verbose_name='Pregunta')),
                ('technician', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='users.technician', verbose_name='Técnico')),
            ],
            options={
                'verbose_name': 'Respuesta del técnico',
                'verbose_name_plural': 'Respuestas de los técnicos',
                'unique_together': {('technician', 'question')},
            },
        ),
    ]
