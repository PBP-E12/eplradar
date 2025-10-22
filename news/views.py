# views.py
from django.shortcuts import get_object_or_404, render
from .models import News

def news_list(request):
    news_items = News.objects.all()

    category = request.GET.get('category')
    sort_by = request.GET.get('sort', '-created_at') 
    
    # --- Filter berdasarkan Kategori ---
    if category and category != 'all':
        news_items = news_items.filter(category=category)
        
    # --- Pengurutan (Sort) ---
    if sort_by == 'views_asc':
        order_field = 'news_views'
    elif sort_by == 'views_desc':
        order_field = '-news_views'
    else:
        order_field = '-created_at'

    news_items = news_items.order_by(order_field)
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