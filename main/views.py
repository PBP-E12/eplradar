from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
import datetime
from news.models import News
from clubs.models import Club 
from django.templatetags.static import static
import csv, os
from django.conf import settings

# Create your views here.
def show_main(request):
    news_terbaru = News.objects.order_by('-created_at')[:3]
    clubs = read_clubs_for_home(limit=4)
    context = {
        'title': 'EPLRadar',
        'news_terbaru': news_terbaru,
        'clubs': clubs,
    }
    return render(request, "main.html", context)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun kamu berhasil dibuat!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def read_clubs_for_home(limit=4):
    clubs = []
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'clubs.csv')

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for idx, row in enumerate(csv_reader, start=1):
                club_name = row['Club_name']
                logo_filename = club_name.replace(' ', '_')
                logo_url = static(f'img/club/{logo_filename}.png')

                win = int(row['Win_count'])
                draw = int(row['Draw_count'])
                lose = int(row['Lose_count'])
                points = win * 3 + draw

                clubs.append({
                    'id': idx,
                    'nama_klub': club_name,
                    'logo_filename': logo_filename,
                    'logo_url': logo_url,
                    'jumlah_win': win,
                    'jumlah_draw': draw,
                    'jumlah_lose': lose,
                    'points': points,
                    'total_matches': win + draw + lose
                })
    except Exception as e:
        print("Error reading clubs for home:", e)

    return clubs[:limit]