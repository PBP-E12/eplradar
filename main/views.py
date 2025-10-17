from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
        'title': 'EPLRadar'
    }

    return render(request, "main.html", context)