from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
        except:
            username = request.POST.get("username")
            password = request.POST.get("password")

        if not username or not password:
            return JsonResponse({
                "login": False,
                "message": "Username and password are required."
            }, status=400)

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                "login": True,
                "username": user.username,
                "message": "Login successful!"
            }, status=200)

        return JsonResponse({
            "login": False,
            "message": "Invalid username or password."
        }, status=401)

    return JsonResponse({
        "login": False,
        "message": "Method not allowed."
    }, status=405)


@csrf_exempt
def register(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
        except:
            data = request.POST

        username = data.get('username')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if not username or not password1 or not password2:
            return JsonResponse({
                "status": False,
                "message": "All fields are required."
            }, status=400)

        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)

        User.objects.create_user(username=username, password=password1)

        return JsonResponse({
            "status": True,
            "message": "User created successfully!"
        }, status=200)

    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=405)

@csrf_exempt
def logout(request):
    if request.method in ["POST", "GET"]:
        auth_logout(request)
        return JsonResponse({
            "status": True,
            "message": "Logout successful"
        })

    return JsonResponse({
        "status": False,
        "message": "Invalid method"
    }, status=405)