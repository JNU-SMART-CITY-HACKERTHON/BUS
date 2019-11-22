from django.shortcuts import render
from .models import Day, Hour, Line


def index(request):
    return render(request, 'main/index.html')

def show(request):
    return render(request, 'main/show.html')
