from django import forms
from .models import User, Course, Semester
from django.core import validators
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import SetPasswordForm


PROGRAM = [
('Bachelor of Laws', 'Bachelor of Laws'),
('Diploma in Paralegal Studies', 'Diploma in Paralegal Studies'),
('Diploma in Law', 'Diploma in Law'),
('Bachelor of Science in Economics', 'Bachelor of Science in Economics'),
('Bachelor of Science in Agriculture Economics', 'Bachelor of Science in Agriculture Economics'),
('Bachelor of Science in Agribusiness', 'Bachelor of Science in Agribusiness'),
('Bachelor of Arts in Environment and Development Studies', 'Bachelor of Arts in Environment and Development Studies'),
('Bachelor of Arts in Communication Studies', 'Bachelor of Arts in Communication Studies'),
('Bachelor of Arts in Theology', 'Bachelor of Arts in Theology'),
('Bachelor of Science in Psychology', 'Bachelor of Science in Psychology'),
('Bachelor of Arts in Sociology', 'Bachelor of Arts in Sociology'),
('Bachelor of Arts in Social Work', 'Bachelor of Arts in Social Work'),
('Bachelor of Arts in French', 'Bachelor of Arts in French'),
('Bachelor of Science in Management Studies', 'Bachelor of Science in Management Studies'),
('Bachelor of Science in Banking and Finance', 'Bachelor of Science in Banking and Finance'),
('Bachelor of Science in Business Administration', 'Bachelor of Science in Business Administration'),
('Doctor of Pharmacy', 'Doctor of Pharmacy'),
('Bachelor of Architecture', 'Bachelor of Architecture'),
('Bachelor of Science in Planning', 'Bachelor of Science in Planning'),
('Bachelor of Science in Real Estate', 'Bachelor of Science in Real Estate'),
('Bachelor of Science in Graphic Design', 'Bachelor of Science in Graphic Design'),
('Bachelor of Science in Fashion Design', 'Bachelor of Science in Fashion Design'),
('Bachelor of Science in Landscape Design', 'Bachelor of Science in Landscape Design'),
('Bachelor of Science in Interior Design', 'Bachelor of Science in Interior Design'),
('Bachelor of Science in Computer Science', 'Bachelor of Science in Computer Science'),
('Bachelor of Science in Civil Engineering', 'Bachelor of Science in Civil Engineering'),
('Bachelor of Science in Information Technology', 'Bachelor of Science in Information Technology'),
('Bachelor of Science in Environmental Engineering', 'Bachelor of Science in Environmental Engineering'),
('Bachelor of Science in Nursing', 'Bachelor of Science in Nursing'),
('Bachelor of Science in Physician Assistantship', 'Bachelor of Science in Physician Assistantship'),
('Bachelor of Science in Public Health', 'Bachelor of Science in Public Health')
]



GRADE = [
		('', '---------'),
        ('4', 'A'),
        ('3.5', 'B+'),
        ('3', 'B'),
        ('2.5', 'C+'),
        ('2', 'C'),
        ('1.5', 'D+'),
        ('1', 'D'),
        ('0', 'F'),
        ]
class NewUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'inp-form',}))
    last_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'inp-form',}))
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'inp-form',}))
    email = forms.CharField(max_length=255, widget=forms.EmailInput(attrs={'class': 'inp-form',}))
    program = forms.ChoiceField(choices=PROGRAM, widget=forms.Select(attrs={'class': 'inp-form'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inp-form',}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'inp-form',}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'program', 'password', 'confirm_password')

    def clean(self):
        cleaned_data = super().clean()

        MIN_PASSWORD_LENGTH = 8
        if len(cleaned_data.get('password')) < MIN_PASSWORD_LENGTH:
            self.add_error('confirm_password', f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email


class CourseForm(forms.ModelForm):
    course_name = forms.CharField(max_length=255)
    course_code = forms.CharField(max_length=255)
    credit_hour = forms.IntegerField(
        validators=[
            MinValueValidator(1, message=('Credit hour must be a positive integer.')),
        ]
        )
    grade = forms.ChoiceField(choices=GRADE, widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, user=None, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['semester'].queryset = Semester.objects.filter(student=user)

    class Meta:
        model = Course
        fields = ('course_name', 'course_code', 'credit_hour', 'grade', 'semester')


class PasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'class': 'inp-form'}))
    new_password2 = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(attrs={'class': 'inp-form'}))

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2