from django.shortcuts import render

def index(request):
    return render(request, 'awesome_app/main.html')