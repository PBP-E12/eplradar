from django.shortcuts import render

# Create your views here.
def show_matches(request):
    return render(request, "show_matches.html")
