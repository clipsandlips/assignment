from django.urls import path
from django.contrib import admin  
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('register/', views.register, name='register'),
    path('quotes/', views.quotes_list, name='quotes_list'),
    path('add-author/', views.add_author, name='add_author'),
    path('add-quote/', views.add_quote, name='add_quote'),
    path('login/', views.login_view, name='login'),   
    path('logout/', views.logout_view, name='logout'), 
    path('search_quotes/', views.search_quotes, name='search_quotes'),
    path('top-ten/', views.top_ten_quotes, name='top_ten_quotes'), 
    path('authors/', views.authors_list, name='authors_list'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
