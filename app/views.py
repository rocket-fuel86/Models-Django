from datetime import datetime
from django.shortcuts import render
from app.models import Category, Product, Manufacturer

def category(request):
    message = None

    if request.method == 'POST' and request.POST.get('action') == 'create':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            Category.objects.create(
                name=name,
                slug=slug,
                description=description,
                created_at=datetime.now(),
            )
            message = f'Категорію "{name}" додано!'
        else:
            message = 'Помилка'

    elif request.method == 'POST' and request.POST.get('action') == 'update':
        category_id = request.POST.get('category_id')
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        created_at = request.POST.get('created_at', '').strip()

        try:
            category = Category.objects.get(id=category_id)
            category.name = name
            category.slug = slug
            category.description = description
            category.created_at = created_at
            category.save()
            message = f'Категорію "{category.name}" оновлено!'
        except Category.DoesNotExist:
            message = 'Автора не знайдено.'

    elif request.method == 'POST' and request.POST.get('action') == 'delete':
        category_id = request.POST.get('category_id')
        try:
            category = Category.objects.get(id=category_id)
            name = category.name
            category.delete()
            message = f'Категорію "{name}" видалено.'
        except Category.DoesNotExist:
            message = 'Категорію не знайдено.'

    categories = Category.objects.all().order_by('id')

    return render(request, 'category.html', {
        'title': 'Категорії',
        'year': datetime.now().year,
        'categories': categories,
        'message': message,
    })

import json

def product(request):
    message = None

    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':

            Product.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),

                description=request.POST.get('description') or '',
                short_description=request.POST.get('short_description') or '',

                category_id=request.POST.get('category'),
                manufacturer_id=request.POST.get('manufacturer') or None,

                price=request.POST.get('price'),
                discount_price=request.POST.get('discount_price') or None,
                stock_quantity=request.POST.get('stock_quantity') or 0,

                sku=request.POST.get('sku'),

                weight=request.POST.get('weight') or None,

                is_available=bool(request.POST.get('is_available')),
                status=request.POST.get('status'),

                tags=json.loads(request.POST.get('tags') or '[]'),
            )

            message = "Продукт створено"

        elif action == 'update':

            obj = Product.objects.get(id=request.POST.get('id'))

            obj.name = request.POST.get('name')
            obj.slug = request.POST.get('slug')
            obj.description = request.POST.get('description')
            obj.short_description = request.POST.get('short_description')

            obj.category_id = request.POST.get('category')
            obj.manufacturer_id = request.POST.get('manufacturer') or None

            obj.price = request.POST.get('price')
            obj.discount_price = request.POST.get('discount_price') or None
            obj.stock_quantity = request.POST.get('stock_quantity') or 0

            obj.sku = request.POST.get('sku')
            obj.weight = request.POST.get('weight') or None

            obj.is_available = True if request.POST.get('is_available') else False
            obj.status = request.POST.get('status')

            obj.tags = json.loads(request.POST.get('tags') or '[]')

            obj.save()

            message = "Оновлено"

        elif action == 'delete':
            Product.objects.filter(id=request.POST.get('id')).delete()
            message = "Видалено"

    products = Product.objects.select_related(
        'category', 'manufacturer'
    ).prefetch_related('additional_categories')

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'message': message
    })

def manufacturer(request):
    message = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Manufacturer.objects.create(
                name=request.POST.get('name'),
                country=request.POST.get('country'),
                website=request.POST.get('website') or None,
                email=request.POST.get('email') or None,
                established_year=request.POST.get('established_year') or None,
            )
            message = "Створено"

        elif action == 'update':
            obj = Manufacturer.objects.get(id=request.POST.get('id'))
            obj.name = request.POST.get('name')
            obj.country = request.POST.get('country')
            obj.website = request.POST.get('website') or None
            obj.email = request.POST.get('email') or None
            obj.established_year = request.POST.get('established_year') or None
            obj.save()
            message = "Оновлено"

        elif action == 'delete':
            Manufacturer.objects.filter(id=request.POST.get('id')).delete()
            message = "Видалено"

    return render(request, 'manufacturer.html', {
        'manufacturers': Manufacturer.objects.all(),
        'message': message
    })