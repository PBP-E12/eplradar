from django.shortcuts import render

def show_clubs(request):
    context = {
        'title': 'EPLRadar'
    }

    return render(request, "clubs.html", context)