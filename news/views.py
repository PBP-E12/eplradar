from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from .models import News


def news_list(request):
    category = request.GET.get('category')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Filter kategori
    news_items = News.objects.all()
    if category and category != 'all':
        news_items = news_items.filter(category=category)

    # Sorting
    if sort_by == 'views_asc':
        order_field = 'news_views'
    elif sort_by == 'views_desc':
        order_field = '-news_views'
    else:
        order_field = '-created_at'
    news_items = news_items.order_by(order_field)

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
                "is_featured": n.is_featured,
                "user_id": n.user.id if n.user else None,
                "username": n.user.username if n.user else "Anonymous",
            })
        return JsonResponse({
            "news_items": data,
            "current_user_id": request.user.id if request.user.is_authenticated else None
        }, status=200)
    
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


@login_required
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
        user=request.user,
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
            "user_id": news.user.id,
            "username": news.user.username,
            "title": news.title,
            "content": news.content,
            "category": news.get_category_display(),
            "thumbnail": news.thumbnail,
            "created_at": news.created_at.strftime("%d %b %Y"),
            "views": news.news_views,
            "is_featured": news.is_featured,
        }
    }, status=201)


@login_required
@csrf_exempt
@require_http_methods(["PUT", "POST"])
def update_news_ajax(request, pk):
    try:
        news = News.objects.get(pk=pk, user=request.user)
    except News.DoesNotExist:
        return JsonResponse({"success": False, "message": "Berita tidak ditemukan atau bukan milik Anda."}, status=404)
    
    title = request.POST.get("title")
    content = request.POST.get("content")
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'
    
    if not title or not content or not category:
        return JsonResponse({"success": False, "message": "Semua field wajib diisi."}, status=400)
    
    news.title = title
    news.content = content
    news.category = category
    news.thumbnail = thumbnail if thumbnail else news.thumbnail
    news.is_featured = is_featured
    news.save()
    
    return JsonResponse({
        "success": True,
        "message": f"Berita '{news.title}' berhasil diperbarui!",
        "news": {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "category": news.get_category_display(),
            "thumbnail": news.thumbnail,
            "created_at": news.created_at.strftime("%d %b %Y"),
            "views": news.news_views,
            "is_featured": news.is_featured,
        }
    }, status=200)


@login_required
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_news_ajax(request, pk):
    try:
        news = News.objects.get(pk=pk, user=request.user)
    except News.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Berita tidak ditemukan atau bukan milik Anda.'}, status=404)

    if request.method == 'DELETE' or request.POST.get('_method') == 'DELETE':
        title = news.title
        news.delete()
        return JsonResponse({'status': 'success', 'message': f'Berita "{title}" telah dihapus.'}, status=200)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
