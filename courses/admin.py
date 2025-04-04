# admin.py
from django.contrib import admin
from .models import Course, Section, Question, Answer, Desempeno, CourseApplication, Region, Instructor

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [AnswerInline]
    show_change_link = True

class CourseApplicationInline(admin.TabularInline):
    model = CourseApplication
    extra = 1
    show_change_link = True

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_hours', 'instructor', 'region', 'created_at')
    list_filter = ('instructor', 'region')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QuestionInline, CourseApplicationInline]

class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'text', 'course__name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'type', 'order', 'course')
    list_filter = ('type', 'course')
    search_fields = ('text', 'course__name')
    ordering = ('course', 'order')

class DesempenoAdmin(admin.ModelAdmin):
    list_display = ['technician', 'course', 'puntuacion', 'fecha', 'estado']
    list_filter = ['estado', 'course', 'technician']
    search_fields = ['technician__name', 'course__name']

# Registrar los modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Answer)
admin.site.register(Region, RegionAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(CourseApplication)
admin.site.register(Desempeno, DesempenoAdmin)