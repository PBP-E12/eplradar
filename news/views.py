import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from .models import News
import requests
from django.utils.html import strip_tags


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
@require_http_methods(["POST"])
def delete_news_ajax(request, pk):
    try:
        news = News.objects.get(pk=pk, user=request.user)
    except News.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Berita tidak ditemukan atau bukan milik Anda.'}, status=404)

    
    title = news.title
    news.delete()
    return JsonResponse({'status': 'success', 'message': f'Berita "{title}" telah dihapus.'}, status=200)


def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def create_news_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = strip_tags(data.get("title", ""))  # Strip HTML tags
        content = strip_tags(data.get("content", ""))  # Strip HTML tags
        category = data.get("category", "")
        thumbnail = data.get("thumbnail", "")
        is_featured = data.get("is_featured", False)
        user = request.user
        
        new_news = News(
            title=title, 
            content=content,
            category=category,
            thumbnail=thumbnail,
            is_featured=is_featured,
            user=user
        )
        new_news.save()
        
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)

def show_json(request):
    news_items = News.objects.all()
    data = [
        {
            'id': n.id,
            'user_id': n.user.id if n.user else None,
            'user': n.user.username if n.user else None,
            'title': n.title,
            'content': n.content,
            'category': n.category,
            'thumbnail': n.thumbnail,
            'news_views': n.news_views,
            'created_at': n.created_at.isoformat() if n.created_at else None,
            'is_featured': n.is_featured,
        }
        for n in news_items
    ]
    return JsonResponse(data, safe=False)