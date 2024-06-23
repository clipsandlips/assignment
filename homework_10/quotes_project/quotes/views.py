from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Quote, Author
from .forms import RegisterForm, SearchForm #, CreateDatabaseForm
from django.db import connection
from django.http import HttpResponseRedirect
#from .scraper import scrape_authors_data, scrape_quotes_data  # Assuming you have a scraper function
from sqlalchemy import create_engine
from django.shortcuts import render
from .forms import AuthorForm, QuoteForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

class QuoteListView(ListView):
    model = Quote
    template_name = 'quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 20

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'author_detail.html'
    context_object_name = 'author'

def index(request):
    return render(request, 'index.html')

def quotes_list(request):
    form = SearchForm()
    quotes = Quote.objects.all()
    paginator = Paginator(quotes, 20)  # Show 20 quotes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tags = get_unique_tags()
    return render(request, 'quote_list.html', {'page_obj': page_obj, 'form': form, 'tags': tags})

def top_ten_quotes(request):
    form = SearchForm()
    top_quotes = Quote.objects.order_by('-id')[:10]
    tags = get_unique_tags()
    return render(request, 'quote_list.html', {'quotes': top_quotes, 'form': form, 'tags': tags})

def authors_list(request):
    authors = Author.objects.all()
    return render(request, 'authors_list.html', {'authors': authors})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, new_user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def search_quotes(request):
    form = SearchForm(request.GET)
    query = request.GET.get('query', '')
    if query:
        quotes = Quote.objects.filter(Q(tags__icontains=query))
    else:
        quotes = Quote.objects.all()
    paginator = Paginator(quotes, 20)  # Show 20 quotes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tags = get_unique_tags()
    return render(request, 'quote_list.html', {'page_obj': page_obj, 'form': form, 'tags': tags})

def get_unique_tags():
    quotes = Quote.objects.values_list('tags', flat=True)
    tags = set()
    for quote_tags in quotes:
        if quote_tags:
            tags.update(tag.strip() for tag in quote_tags.split(','))
    return sorted(tags)

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            return redirect('home')  # Redirect to the index or another page
    else:
        form = AuthorForm()
    
    return render(request, 'add_author.html', {'form': form})

@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save()
            return redirect('home')  # Redirect to the index or another page
    else:
        form = QuoteForm()
    
    return render(request, 'add_quote.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to main page after successful login
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


#def scrape_and_save_data(request):
#    db_name = request.POST.get('db_name')  # Assuming you have a form to provide DB name
#    authors_data = scrape_authors_data()
#    quotes_data = scrape_quotes_data()

#    for author_data in authors_data:
#        author = Author(fullname=author_data['fullname'])
#        author.save()

#    for quote_data in quotes_data:
#        author = Author.objects.get(fullname=quote_data['author'])
#        quote = Quote(text=quote_data['quote'], author=author)
#        quote.save()

#    return render(request, 'success.html', {'message': 'Data scraped and saved successfully!'})