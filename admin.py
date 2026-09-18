from django.contrib import admin
from .models import Course
from .models import Lesson
from .models import Instructor
from .models import Learner
from .models import Question
from .models import Choice
from .models import Submission


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# -----------------------------------------------------------------
# TASK: ChoiceInline
# Lets you edit Choices directly inside a Question's admin page.
# -----------------------------------------------------------------
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4


# -----------------------------------------------------------------
# TASK: QuestionInline
# Lets you edit Questions directly inside a Course's admin page.
# -----------------------------------------------------------------
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# -----------------------------------------------------------------
# TASK: LessonAdmin
# -----------------------------------------------------------------
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')


# -----------------------------------------------------------------
# TASK: QuestionAdmin
# Shows Choices inline within each Question's admin page.
# -----------------------------------------------------------------
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('question_text', 'course', 'question_grade')


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission)
