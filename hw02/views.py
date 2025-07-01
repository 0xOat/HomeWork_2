from django.shortcuts import render

def index(request):
    return render(request, "hw02/home.html")