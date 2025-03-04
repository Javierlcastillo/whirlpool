# admin.py
from django.contrib import admin
from .models import Course, Section, Question, Answer, TechnicianProgress, QuestionResponse

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ['text', 'image', 'is_correct']

class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'text', 'course__title']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'text', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'text', 'course__title']
    inlines = [AnswerInline]

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['title', 'text', 'image', 'video_url', 'order']
    show_change_link = True

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['title', 'text', 'image', 'order']
    show_change_link = True

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration_weeks', 'category', 'created_at']
    list_filter = ['category', 'instructor']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline, QuestionInline]

class TechnicianProgressAdmin(admin.ModelAdmin):
    list_display = ['technician', 'course', 'completed', 'score', 'started_at', 'completed_at']
    list_filter = ['completed', 'course', 'technician']
    search_fields = ['technician__user__first_name', 'technician__user__last_name', 'course__title']

class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ['technician', 'question', 'is_correct', 'response_time']
    list_filter = ['is_correct', 'question__course', 'technician']
    search_fields = ['technician__user__first_name', 'technician__user__last_name', 'question__text']

# Registrar los modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(TechnicianProgress, TechnicianProgressAdmin)
admin.site.register(QuestionResponse, QuestionResponseAdmin)