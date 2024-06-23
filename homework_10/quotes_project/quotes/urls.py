from django.urls import path
from django.contrib import admin  # Import Django's admin module
from django.urls import include  # Import include for including admin URLs
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
    #path('create-database-and-scrape/', views.create_database_and_scrape, name='create_database_and_scrape'),
]





