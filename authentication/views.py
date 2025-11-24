from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def login(request):
    # Cek apakah method POST
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validasi input tidak kosong
        if not username or not password:
            return JsonResponse({
                "status": False,
                "message": "Username and password are required."
            }, status=400)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                
                # ✅ Checklist 3: Cek otorisasi/role
                is_admin = user.is_staff or user.is_superuser
                
                # Login status successful.
                return JsonResponse({
                    "username": user.username,
                    "status": True,
                    "message": "Login successful!",
                    "is_admin": is_admin,  # Tambahan untuk cek role
                }, status=200)
            else:
                return JsonResponse({
                    "status": False,
                    "message": "Login failed, account is disabled."
                }, status=401)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, please check your username or password."
            }, status=401)
    
    # Jika bukan POST
    return JsonResponse({
        "status": False,
        "message": "Method not allowed. Please use POST."
    }, status=405)