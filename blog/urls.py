from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('post/<slug:slug>/', views.post, name="post"),
    path('post-detail/<int:pk>/', views.post_detail, name="post_detail"),  # Добавь эту строку
    path('category/<slug:slug>/', views.category, name="category"),
    path('search/', views.search, name="search"),
    path('create/', views.PostCreateView.as_view(), name="create"),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='blog_login'),
    path('logout/', views.custom_logout_view, name='blog-logout'),
]