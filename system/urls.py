"""
URL configuration for system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_view
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.viewBoard, name='viewboard'),
    path('course', views.course, name='course'),
    path('addcourse', views.addcourse, name='addcourse'),
    path('addSem', views.addSem, name='addSem'),
    path('retaken/<int:pk>/', views.retaken, name='retaken'),
    path('gradcal', views.gradcal, name='gradcal'),
    path('termcal', views.termcal, name='termcal'),
    path('registeruser/', views.register_view, name='newuser'),
    # path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    # path('deleteSem/<int:pk>/', views.deleteSem, name='deleteSem'),
	path('login/', views.login_view, name='login'),
    path('reset', views.reset, name='reset'),
    path('reset_password/<str:uidb64>/<str:token>/', views.PasswordResetConfirmView.as_view(), name='reset_password'),
	path('logout/', auth_view.LogoutView.as_view(template_name='core/logout.html'), name='logout'),
]
