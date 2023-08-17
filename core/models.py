from django.contrib.auth.models import User as BaseUser
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
PROGRAM = (
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
)


GRADE = (
        ('4', 'A'),
        ('3.5', 'B+'),
        ('3', 'B'),
        ('2.5', 'C+'),
        ('2', 'C'),
        ('1.5', 'D+'),
        ('1', 'D'),
        ('0', 'F'),
        )
class User(BaseUser):
        program = models.CharField(max_length=255, choices=PROGRAM)

        def __str__(self):
        	return self.username

class Semester(models.Model):
        student = models.ForeignKey(User, on_delete=models.CASCADE)
        semester = models.IntegerField(default=0)
        gpa = models.FloatField(default=0)

        def __str__(self):
                return f'Semester {self.semester}'

class Course(models.Model):
        course_name = models.CharField(max_length=255)
        course_code = models.CharField(max_length=255)
        credit_hour = models.IntegerField(default=0)
        grade = models.CharField(max_length=15, choices=GRADE)
        grade_point = models.FloatField(default=0)
        student = models.ForeignKey(User, on_delete=models.CASCADE)
        resit = models.BooleanField(default=True)
        semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

        def __str__(self):
                return self.course_name