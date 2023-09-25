from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CustomRegistrationForm, CustomLoginForm

def index(request):
    return render(request, 'awesome_app/main.html')

def register(request):
    error_message = ''

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            error_message = "이미 존재하는 아이디입니다."
        elif form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user = User.objects.create_user(username=username, password=password1)
                if user is not None:
                    login(request, user)
                    return redirect('awesome_app:login')
            else:
                form.add_error('password2', 'Passwords do not match')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form, 'error_message': error_message})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CustomLoginForm(data=request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('awesome_app:main')
    return render(request, 'registration/login.html', {'form': form})

def logout(request):
    logout(request)
    return render(request, "awesome_app/main.html")

def trade(request):
    return render(request, 'awesome_app/trade.html')

def trade_post(request):
    return render(request, 'awesome_app/trade_post.html')

def write(request):
    return render(request, 'awesome_app/write.html')

def search(request):
    posts = []
    return render(request, 'awesome_app/search.html', {"posts": posts})

def location(request):
    return render(request, 'awesome_app/location.html')

def chat(request):
    region = ''
    return render(request, 'awesome_app/chat.html', {"region" : region})