from django.shortcuts import render

def index(request):
    return render(request, 'awesome_app/main.html')

def login(request):
    return render(request, 'registration/login.html', )

def logout(request):
    logout(request)
    return render(request, "awesome_app/main.html")

def register(request):
    return render(request, 'registration/register.html')

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