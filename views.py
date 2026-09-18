import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.conf import settings

from .models import Course, Enrollment, Question, Choice, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                num_enrollments = Enrollment.objects.filter(user=user, course=course).count()
                course.is_enrolled = num_enrollments > 0
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = Course.objects.get(pk=course_id)
    user = request.user

    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# -----------------------------------------------------------------
# TASK: submit view
# Creates a Submission for the learner's current enrollment,
# collects every selected choice from the exam form, attaches
# them to the submission, and redirects to show_exam_result.
# -----------------------------------------------------------------
@login_required
def submit(request, course_id):
    course = Course.objects.get(pk=course_id)
    user = request.user

    # Get the current enrollment for the user and course
    enrollment = Enrollment.objects.get(user=user, course=course)

    # Create a new Submission record
    submission = Submission.objects.create(enrollment=enrollment)

    # Collect the selected choice ids from the submitted form
    selected_choices = extract_answers(request)
    for choice_id in selected_choices:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)

    submission.save()

    return HttpResponseRedirect(
        reverse(
            viewname='onlinecourse:exam_result',
            args=(course.id, submission.id)
        )
    )


def extract_answers(request):
    """
    Helper: collects every checkbox input whose name starts with
    'choice' from the submitted exam form and returns a list of
    the selected choice ids (as integers).
    """
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers


# -----------------------------------------------------------------
# TASK: show_exam_result view
# Looks up the submission, figures out which questions were
# answered fully correctly, sums the grade, and renders the
# exam result template with the score and pass/fail state.
# -----------------------------------------------------------------
def show_exam_result(request, course_id, submission_id):
    course = Course.objects.get(pk=course_id)
    submission = Submission.objects.get(pk=submission_id)
    selected_choices = submission.choices.all()
    selected_choice_ids = [choice.id for choice in selected_choices]

    total_score = 0
    questions = Question.objects.filter(course=course)

    for question in questions:
        if question.is_get_score(selected_choice_ids):
            total_score += question.question_grade

    context = {
        'course': course,
        'submission': submission,
        'selected_choices': selected_choices,
        'grade': total_score,
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
