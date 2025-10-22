from django.shortcuts import render

# Create your views here.
def show_detail(request):
    context = {
        "name" : "Oscar",
    }
    
    return render(request, "show_detail.html", context)
