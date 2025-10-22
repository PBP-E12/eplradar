# views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import News
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def news_list(request):
    category = request.GET.get('category')
    sort_by = request.GET.get('sort', '-created_at')

    # Filter kategori
    news_items = News.objects.all()
    if category and category != 'all':
        news_items = news_items.filter(category=category)

    # Urutkan
    if sort_by == 'views_asc':
        order_field = 'news_views'
    elif sort_by == 'views_desc':
        order_field = '-news_views'
    else:
        order_field = '-created_at'
    news_items = news_items.order_by(order_field)

    # Jika AJAX request → return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for n in news_items:
            data.append({
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "category": n.category,
                "category_display": n.get_category_display(), 
                "thumbnail": n.thumbnail,
                "created_at": n.created_at.strftime("%d %b %Y"),
                "views": n.news_views,
            })
        return JsonResponse({"news_items": data}, status=200)
    
    context = {
        'news_items': news_items,
        'category_choices': News.CATEGORY_CHOICES,
        'current_category': category,
        'current_sort': sort_by,
    }
    return render(request, 'news.html', context)


def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    news_item.increment_views()
    
    return render(request, 'news_detail.html', {'news_item': news_item})

@csrf_exempt
@require_POST
def add_news_ajax(request):
    title = request.POST.get("title")
    content = request.POST.get("content")
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'

    if not title or not content or not category:
        return JsonResponse({"success": False, "message": "Semua field wajib diisi."}, status=400)

    news = News.objects.create(
        title=title,
        content=content,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
    )
    return JsonResponse({
        "success": True,
        "message": "Berita berhasil ditambahkan!",
        "news": {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "category": news.get_category_display(),
            "thumbnail": news.thumbnail,
            "created_at": news.created_at.strftime("%d %b %Y"),
            "views": news.news_views,
        }
    }, status=201)