from django.contrib import admin
from .models import Course, Question, Answer, FAQ

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ['text', 'image', 'is_correct']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'course', 'order']
    list_filter = ['course']
    search_fields = ['text', 'course__title']
    inlines = [AnswerInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'image', 'order']
    show_change_link = True

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration_weeks', 'category', 'created_at']
    list_filter = ['category', 'instructor']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]

class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order']
    list_editable = ['order']
    search_fields = ['question', 'answer']

# Registrar los modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(FAQ, FAQAdmin)