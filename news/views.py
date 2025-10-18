from django.shortcuts import render

# fungsi untuk test doang
def show_news(request):
    context = {
        'news' : "news"
    }
    return render(request, "news.html", context)