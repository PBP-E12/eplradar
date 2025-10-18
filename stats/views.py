from django.shortcuts import render

# Create your views here.
def show_stats(request):
    context = {
        'title': 'Stats Corner',
    }

    return render(request, "main.html", context)