from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import NewUserForm, CourseForm, PasswordResetForm
from django.contrib import messages
from .models import User, Course, Semester
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views import View
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        try:
        	email = User.objects.get(email=request.POST.get('username').lower())
        except User.DoesNotExist:
            messages.error(request, 'Invalid login credentials.', extra_tags='alert alert-warning')
            return redirect('login')
        username = email.username.lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                login(request, user)
                return redirect('viewboard')
            except User.DoesNotExist:
                    messages.error(request, 'Student account does not exist', extra_tags='alert alert-info')
                    return redirect('login')
        elif not username:
            messages.error(request, 'Enter login credentials.', extra_tags='alert alert-warning')
            return redirect('login')
        else:
            messages.error(request, 'Invalid login credentials.', extra_tags='alert alert-warning')
            return redirect('login')
    return render(request, 'core/login.html')

def register_view(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            messages.success(request, 'Account created successfully.', extra_tags='alert alert-success')
            return redirect('login')
    else:
        form = NewUserForm()

    context = {
        'form': form,
    }

    return render(request, 'core/register.html', context)

@login_required
def addcourse(request):
    usr = request.user
    user = User.objects.get(username=usr)
    if request.method == 'POST':
        form = CourseForm(request.POST, user=user)
        if form.is_valid():
            course = form.save(commit=False)
            course.student = user
            course.grade_point = course.credit_hour * float(course.grade)
            if course.grade_point == 0.0:
                course.resit = False
            course.save()
            messages.success(request, 'Course added successfully.', extra_tags='alert alert-success')
            return redirect('course')
    else:
        form = CourseForm(user=user)

    context = {
    'form': form,
    }
    return render(request, 'core/course.html', context)


def retaken(request, pk):
    course = Course.objects.get(id=pk)
    course.resit = True
    course.save()
    return redirect('course')

@login_required
def termcal(request):
    usr = request.user
    user = User.objects.get(username=usr)
    courses = Course.objects.filter(student=user)
    tot_grade_point = 0
    tot_credit = 0
    applied_ch = 0
    cgpa = 0
    new_gpa = 0

    for course in  courses:
        tot_credit += course.credit_hour
        grade_point = float(course.grade) * course.credit_hour
        tot_grade_point += grade_point
        cgpa = tot_grade_point / tot_credit

    for course in courses:
        applied_ch += course.credit_hour

    if request.method == 'POST':
        total_credit = 0
        total_weighted_grade_points = 0
        for i in range(1, 11):
            course_name = request.POST.get(f'course{i}')
            credit_str = request.POST.get(f'credit{i}')
            grade_str = request.POST.get(f'grade{i}')

            if course_name and credit_str and grade_str:
                credit = float(credit_str)
                grade = float(grade_str)

                total_credit += credit
                total_weighted_grade_points += credit * grade
        if total_credit != 0:
            new_gpa = (total_weighted_grade_points + tot_grade_point ) / (total_credit + tot_credit)
        else:
            new_gpa = 0

        context = {
        'cgpa': cgpa,
        'new_gpa': new_gpa,
        'applied_ch': applied_ch
        }

        return render(request, 'core/term_calc.html', context)

    context = {
    'cgpa': cgpa,
    'new_gpa': new_gpa,
    'applied_ch': applied_ch
    }

    return render(request, 'core/term_calc.html', context)


@login_required
def gradcal(request):
    usr = request.user
    user = User.objects.get(username=usr)
    courses = Course.objects.filter(student=user)
    tot_grade_point = 0
    tot_credit = 0
    required_ch = 0
    applied_ch = 0
    cgpa = 0

    PROGRAM = {
    'Bachelor of Laws': 120,
    'Diploma in Paralegal Studies': 60,
    'Diploma in Law': 60,
    'Bachelor of Science in Economics': 120,
    'Bachelor of Science in Agriculture Economics': 120,
    'Bachelor of Science in Agribusiness': 120,
    'Bachelor of Arts in Environment and Development Studies': 120,
    'Bachelor of Arts in Communication Studies': 120,
    'Bachelor of Arts in Theology': 120,
    'Bachelor of Science in Psychology': 120,
    'Bachelor of Arts in Sociology': 120,
    'Bachelor of Arts in Social Work': 120,
    'Bachelor of Arts in French': 120,
    'Bachelor of Science in Management Studies': 120,
    'Bachelor of Science in Banking and Finance':120,
    'Bachelor of Science in Business Administration': 120,
    'Doctor of Pharmacy': 150,
    'Bachelor of Architecture': 120,
    'Bachelor of Science in Planning':120,
    'Bachelor of Science in Real Estate': 120,
    'Bachelor of Science in Graphic Design': 120,
    'Bachelor of Science in Fashion Design': 120,
    'Bachelor of Science in Landscape Design': 120,
    'Bachelor of Science in Interior Design': 120,
    'Bachelor of Science in Computer Science': 120,
    'Bachelor of Science in Civil Engineering': 120,
    'Bachelor of Science in Information Technology': 120,
    'Bachelor of Science in Environmental Engineering': 120,
    'Bachelor of Science in Nursing': 120,
    'Bachelor of Science in Physician Assistantship': 120,
    'Bachelor of Science in Public Health': 120
    }

    if user.program in PROGRAM:
        required_ch = PROGRAM[user.program]

    for course in courses:
        applied_ch += course.credit_hour

    remainder_ch = required_ch - applied_ch

    for course in  courses:
        tot_credit += course.credit_hour
        grade_point = float(course.grade) * course.credit_hour
        tot_grade_point += grade_point
        cgpa = tot_grade_point / tot_credit

    # if request.method == 'POST':
    #     desired_gpa = request.POST.get(name="desired_gpa")

    #     pro = ((desired_gpa * required_ch) - (cgpa * applied_ch)) / remainder_ch

    context = {
    'cgpa': cgpa,
    'user': user,
    'required_ch': required_ch,
    'remainder_ch': remainder_ch,
    }

    return render(request, 'core/grad_calc.html', context)


@login_required
def course(request):
    usr = request.user
    user = User.objects.get(username=usr)
    sems = Semester.objects.filter(student=user)
    courses = Course.objects.filter(student=user)
    tot_grade_point = 0
    tot_credit = 0
    sem_grade_point1 = 0
    sem_credit1 = 0
    sem_grade_point2 = 0
    sem_credit2 = 0
    sem_grade_point3 = 0
    sem_credit3 = 0
    sem_grade_point4 = 0
    sem_credit4 = 0
    sem_grade_point5 = 0
    sem_credit5 = 0
    sem_grade_point6 = 0
    sem_credit6 = 0
    sem_grade_point7 = 0
    sem_credit7 = 0
    sem_grade_point8 = 0
    sem_credit8 = 0
    sem_grade_point9 = 0
    sem_credit9 = 0
    sem_grade_point10 = 0
    sem_credit10 = 0
    sem_grade_point11 = 0
    sem_credit11 = 0
    sem_grade_point12 = 0
    sem_credit12 = 0
    cgpa = 0
    gpa1 = 0
    gpa2 = 0
    gpa3 = 0
    gpa4 = 0
    gpa5 = 0
    gpa6 = 0
    gpa7 = 0
    gpa8 = 0
    gpa9 = 0
    gpa10 = 0
    gpa11 = 0
    gpa12 = 0

    for gpasem in courses:
        if gpasem.semester.semester == 1:
            sem_credit1 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point1 += semone_gp
            gpa1 = sem_grade_point1 / sem_credit1
        if gpasem.semester.semester == 2:
            sem_credit2 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point2 += semone_gp
            gpa2 = sem_grade_point2 / sem_credit2
        if gpasem.semester.semester == 3:
            sem_credit3 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point3 += semone_gp
            gpa3 = sem_grade_point3 / sem_credit3
        if gpasem.semester.semester == 4:
            sem_credit4 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point4 += semone_gp
            gpa4 = sem_grade_point4 / sem_credit4
        if gpasem.semester.semester == 5:
            sem_credit5 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point5 += semone_gp
            gpa5 = sem_grade_point5 / sem_credit5
        if gpasem.semester.semester == 6:
            sem_credit6 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point6 += semone_gp
            gpa6 = sem_grade_point6 / sem_credit6
        if gpasem.semester.semester == 7:
            sem_credit7 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point7 += semone_gp
            gpa7 = sem_grade_point7 / sem_credit7
        if gpasem.semester.semester == 8:
            sem_credit8 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point8 += semone_gp
            gpa8 = sem_grade_point8 / sem_credit8
        if gpasem.semester.semester == 9:
            sem_credit9 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point9 += semone_gp
            gpa9 = sem_grade_point9 / sem_credit9
        if gpasem.semester.semester == 10:
            sem_credit10 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point10 += semone_gp
            gpa10 = sem_grade_point10 / sem_credit10
        if gpasem.semester.semester == 11:
            sem_credit11 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point11 += semone_gp
            gpa11 = sem_grade_point11 / sem_credit11
        if gpasem.semester.semester == 12:
            sem_credit12 += gpasem.credit_hour
            semone_gp = float(gpasem.grade) * gpasem.credit_hour
            sem_grade_point12 += semone_gp
            gpa12 = sem_grade_point12 / sem_credit12


    for course in  courses:
        tot_credit += course.credit_hour
        grade_point = float(course.grade) * course.credit_hour
        tot_grade_point += grade_point
        cgpa = tot_grade_point / tot_credit

    if request.method == 'POST':
        form = CourseForm(request.POST, user=user)
        if form.is_valid():
            course = form.save(commit=False)
            course.student = user
            course.grade_point = course.credit_hour * float(course.grade)
            course.save()
            messages.success(request, 'Course added successfully.', extra_tags='alert alert-success')
            return redirect('addcourse')
    else:
        form = CourseForm(user=user)

    context = {
        'cgpa': cgpa,
        'gpa1': gpa1,
        'gpa2': gpa2,
        'gpa3': gpa3,
        'gpa4': gpa4,
        'gpa5': gpa5,
        'gpa6': gpa6,
        'gpa7': gpa7,
        'gpa8': gpa8,
        'gpa9': gpa9,
        'gpa10': gpa10,
        'gpa11': gpa11,
        'gpa12': gpa12,
        'user': user,
        'form': form,
        'sems': sems,
        'courses': courses,
    }

    return render(request, 'core/course.html', context)


@login_required
def addSem(request):
	usr = request.user
	user = User.objects.get(username=usr)
	sem = Semester.objects.filter(student=user).count()
	PROGRAM = {
    'Bachelor of Laws': 8,
    'Diploma in Paralegal Studies': 4,
    'Diploma in Law': 4,
    'Bachelor of Science in Economics': 8,
    'Bachelor of Science in Agriculture Economics': 8,
    'Bachelor of Science in Agribusiness': 8,
    'Bachelor of Arts in Environment and Development Studies': 8,
    'Bachelor of Arts in Communication Studies': 8,
    'Bachelor of Arts in Theology': 8,
    'Bachelor of Science in Psychology': 8,
    'Bachelor of Arts in Sociology': 8,
    'Bachelor of Arts in Social Work': 8,
    'Bachelor of Arts in French': 8,
    'Bachelor of Science in Management Studies': 8,
    'Bachelor of Science in Banking and Finance': 8,
    'Bachelor of Science in Business Administration': 8,
    'Doctor of Pharmacy': 10,
    'Bachelor of Architecture': 8,
    'Bachelor of Science in Planning': 8,
    'Bachelor of Science in Real Estate': 8,
    'Bachelor of Science in Graphic Design': 8,
    'Bachelor of Science in Fashion Design': 8,
    'Bachelor of Science in Landscape Design': 8,
    'Bachelor of Science in Interior Design': 8,
    'Bachelor of Science in Computer Science': 8,
    'Bachelor of Science in Civil Engineering': 8,
    'Bachelor of Science in Information Technology': 8,
    'Bachelor of Science in Environmental Engineering': 8,
    'Bachelor of Science in Nursing': 8,
    'Bachelor of Science in Physician Assistantship': 8,
    'Bachelor of Science in Public Health': 8
}

	if user.program in PROGRAM:
		if sem < PROGRAM[user.program]:
			newSem = Semester(student=user, semester=(sem+1))
			newSem.save()
			
	return redirect('course')

@login_required
def viewBoard(request):
    usr = request.user
    user = User.objects.get(username=usr)
    registed_course = Course.objects.filter(student=user)
    tot_grade_point = 0
    failed_courses = {}
    tot_credit = 0
    passed_course = 0
    failed_course = 0
    required_ch = 0
    applied_ch = 0
    cgpa = 0

    PROGRAM = {
    'Bachelor of Laws': 120,
    'Diploma in Paralegal Studies': 60,
    'Diploma in Law': 60,
    'Bachelor of Science in Economics': 120,
    'Bachelor of Science in Agriculture Economics': 120,
    'Bachelor of Science in Agribusiness': 120,
    'Bachelor of Arts in Environment and Development Studies': 120,
    'Bachelor of Arts in Communication Studies': 120,
    'Bachelor of Arts in Theology': 120,
    'Bachelor of Science in Psychology': 120,
    'Bachelor of Arts in Sociology': 120,
    'Bachelor of Arts in Social Work': 120,
    'Bachelor of Arts in French': 120,
    'Bachelor of Science in Management Studies': 120,
    'Bachelor of Science in Banking and Finance':120,
    'Bachelor of Science in Business Administration': 120,
    'Doctor of Pharmacy': 150,
    'Bachelor of Architecture': 120,
    'Bachelor of Science in Planning':120,
    'Bachelor of Science in Real Estate': 120,
    'Bachelor of Science in Graphic Design': 120,
    'Bachelor of Science in Fashion Design': 120,
    'Bachelor of Science in Landscape Design': 120,
    'Bachelor of Science in Interior Design': 120,
    'Bachelor of Science in Computer Science': 120,
    'Bachelor of Science in Civil Engineering': 120,
    'Bachelor of Science in Information Technology': 120,
    'Bachelor of Science in Environmental Engineering': 120,
    'Bachelor of Science in Nursing': 120,
    'Bachelor of Science in Physician Assistantship': 120,
    'Bachelor of Science in Public Health': 120
    }

    if user.program in PROGRAM:
        required_ch = PROGRAM[user.program]

    for course in  registed_course:
        tot_credit += course.credit_hour
        grade_point = float(course.grade) * course.credit_hour
        tot_grade_point += grade_point
        cgpa = tot_grade_point / tot_credit

    for course in registed_course:
        if course.grade_point == 0 and course.resit == False:
            failed_course += 1
            failed_courses[course.course_code] = course.course_name
        else:
            passed_course += 1

    for course in registed_course:
        applied_ch += course.credit_hour

    remainder_ch = int(required_ch) - int(applied_ch)
    projectedGpa = ((cgpa * applied_ch) + (1.50 * remainder_ch))/required_ch

    progressbar = 0
    if not failed_courses:
        progressbar = 33.3
    
    if required_ch == 0:
        progressbar += 33.3
    
    if projectedGpa >= 1.50:
        progressbar += 33.3


    context = {
    'cgpa': cgpa,
    'user': user,
    'applied_ch': applied_ch,
    'required_ch': required_ch,
    'remainder_ch': remainder_ch,
    'projectedGpa': projectedGpa,
    'failed_courses': failed_courses,
    'failed_course': failed_course,
    'passed_course': passed_course,
    'progressbar': round(progressbar),
    'registed_course': registed_course.count(),
    'registed_courses': registed_course
    }

    return render(request, 'core/views.html', context)

@login_required
def delete(request, pk):
    item = Course.objects.get(id=pk)
    item.delete()
    return redirect('course')

@login_required
def logout(request):
	return redirect('login')


# @login_required
# def deleteSem(request, pk):
#     item = Semester.objects.get(id=pk)
#     item.delete()
#     return redirect('course')


# @login_required
# def update(request, pk):
#     course = Course.objects.get(id=pk)
#     form = CourseForm(instance=course)
#     if request.method == 'POST':
#         form = CourseForm(request.POST, instance=course)
#         if form.is_valid():
#             crse = form.save(commit=False)
#             crse.grade_point = crse.credit_hour * float(crse.grade)
#             crse.save()
#             messages.success(request, 'Updated successfully', extra_tags='alert alert-success')
#             return redirect('home')
#     context = {
#       'form': form,
#       }
#     return render(request, 'core/addCourse.html', context)



def reset(request):
    if request.method == 'POST':
        usr = request.POST.get('username').lower()
        try:
            user = User.objects.get(email=usr)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_password_link = request.build_absolute_uri(reverse_lazy('reset_password', kwargs={'uidb64': uidb64, 'token': token}))

            subject = "Password Reset"
            message = f'Please click on the link to reset your password: {reset_password_link}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            messages.success(request, 'A reset link has been sent to your email', extra_tags='alert alert-success')
            return redirect('login')
        except User.DoesNotExist:
            pass
            messages.error(request, 'Email address not found', extra_tags='alert alert-warning')
    return render(request, 'core/reset.html')

class PasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = PasswordResetForm(user=user)
            context = {
                'form': form,
                'uidb64': uidb64,
                'token': token,
            }
            return render(request, 'core/resetPassword.html', context)

        else:
            messages.error(request, 'Password reset link invalid', extra_tags='alert alert-warning')
            return redirect('reset')

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            form = PasswordResetForm(user=user, data=request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, 'Password reset successful', extra_tags='alert alert-success')
                return redirect('login')

            else:
                return render(request, 'core/resetPassword.html', {'form': form, 'uidb64': uidb64, 'token': token})

        else:
            messages.error(request, 'Password reset link invalid', extra_tags='alert alert-warning')
            return redirect('reset')