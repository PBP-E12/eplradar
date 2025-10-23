from django.shortcuts import render

# Create your views here.
def show_matches(request):
    context = {
        "name" : "Oscar",
    }
    
    return render(request, "show_detail.html", context)
