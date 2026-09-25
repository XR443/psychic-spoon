from django.shortcuts import render
from django.http import HttpResponse
from .models import User

# Create your views here.
def index(request):
    saved_user = None
    error = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            saved_user = User(name=name)
            saved_user.save()
        else:
            error = "Пожалуйста, введите имя."

    return render(request, "index.html", {
        "user": saved_user,
        "error": error,
    })
