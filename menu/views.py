from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem


def menu_list(request):
    categories = Category.objects.prefetch_related('items').all()
    popular_items = MenuItem.objects.filter(is_popular=True, is_available=True).select_related('category')
    # Hero slider: popular items with real images
    hero_items = (
        MenuItem.objects
        .filter(is_popular=True, is_available=True)
        .exclude(image='')
        .select_related('category')[:6]
    )
    return render(request, 'menu/menu_list.html', {
        'categories': categories,
        'popular_items': popular_items,
        'hero_items': hero_items,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = category.items.filter(is_available=True)
    return render(request, 'menu/category_detail.html', {
        'category': category,
        'items': items,
    })
