"""from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Quote, Source
import random

def random_quote(request):
    # Получаем случайную цитату с учетом веса
    quotes = list(Quote.objects.all())
    weights = [q.weight for q in quotes]
    
    if quotes:
        quote = random.choices(quotes, weights=weights, k=1)[0]
        quote.views += 1
        quote.save()
    else:
        quote = None
    
    return render(request, 'random_quote.html', {'quote': quote})

def like_quote(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    quote.likes += 1
    quote.save()
    return JsonResponse({'likes': quote.likes})

def dislike_quote(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    quote.dislikes += 1
    quote.save()
    return JsonResponse({'dislikes': quote.dislikes})

def add_quote(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        source_name = request.POST.get('source')
        source_type = request.POST.get('source_type')
        weight = int(request.POST.get('weight', 1))
        
        # Создаем или получаем источник
        source, created = Source.objects.get_or_create(
            name=source_name,
            defaults={'type': source_type}
        )
        
        # Создаем цитату
        quote = Quote(text=text, source=source, weight=weight)
        quote.save()
        
        return redirect('random_quote')
    
    return render(request, 'add_quote.html')

def popular_quotes(request):
    quotes = Quote.objects.all().order_by('-likes')[:10]
    return render(request, 'popular_quotes.html', {'quotes': quotes})"""

from django.db import models  # ← ДОБАВЬ ЭТУ СТРОЧКУ!

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from .models import Quote, Source
import random

def random_quote(request):
    quotes = list(Quote.objects.all())
    
    if quotes:
        # Выборка с учетом веса
        weights = [q.weight for q in quotes]
        quote = random.choices(quotes, weights=weights, k=1)[0]
        quote.views += 1
        quote.save()
    else:
        quote = None
    
    return render(request, 'random_quote.html', {'quote': quote})

def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    quote.likes += 1
    quote.save()
    return JsonResponse({'likes': quote.likes})

def dislike_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    quote.dislikes += 1
    quote.save()
    return JsonResponse({'dislikes': quote.dislikes})

def add_quote(request):
    if request.method == 'POST':
        text = request.POST.get('text').strip()
        source_name = request.POST.get('source').strip()
        source_type = request.POST.get('source_type')
        weight = int(request.POST.get('weight', 1))
        
        # Проверка на дубликат
        if Quote.objects.filter(text__iexact=text).exists():
            messages.error(request, 'Такая цитата уже существует!')
            return redirect('add_quote')
        
        # Создаем или получаем источник
        source, created = Source.objects.get_or_create(
            name=source_name,
            defaults={'type': source_type}
        )
        
        # Проверяем ограничение в 3 цитаты на источник
        if Quote.objects.filter(source=source).count() >= 3:
            messages.error(request, f'У источника "{source_name}" уже есть 3 цитаты!')
            return redirect('add_quote')
        
        # Создаем цитату
        try:
            quote = Quote(text=text, source=source, weight=weight)
            quote.save()
            messages.success(request, 'Цитата успешно добавлена!')
            return redirect('random_quote')
        except IntegrityError:
            messages.error(request, 'Ошибка при добавлении цитаты!')
    
    return render(request, 'add_quote.html')

def popular_quotes(request):
    quotes = Quote.objects.all().order_by('-likes')[:10]
    return render(request, 'popular_quotes.html', {'quotes': quotes})

def dashboard(request):
    # Статистика для дашборда
    total_quotes = Quote.objects.count()
    total_sources = Source.objects.count()
    total_views = sum(quote.views for quote in Quote.objects.all())
    total_likes = sum(quote.likes for quote in Quote.objects.all())
    
    # Самые популярные источники
    popular_sources = Source.objects.annotate(
        total_quotes=models.Count('quote'),
        total_likes=models.Sum('quote__likes')
    ).order_by('-total_likes')[:5]
    
    # Фильтрация
    source_type = request.GET.get('type', '')
    min_likes = request.GET.get('min_likes', 0)
    
    filtered_quotes = Quote.objects.all()
    
    if source_type:
        filtered_quotes = filtered_quotes.filter(source__type=source_type)
    
    if min_likes:
        filtered_quotes = filtered_quotes.filter(likes__gte=int(min_likes))
    
    filtered_quotes = filtered_quotes.order_by('-likes')[:20]
    
    context = {
        'total_quotes': total_quotes,
        'total_sources': total_sources,
        'total_views': total_views,
        'total_likes': total_likes,
        'popular_sources': popular_sources,
        'filtered_quotes': filtered_quotes,
        'source_type': source_type,
        'min_likes': min_likes,
    }
    
    return render(request, 'dashboard.html', context)

"""def dashboard(request):
    # Статистика для дашборда
    total_quotes = Quote.objects.count()
    total_sources = Source.objects.count()
    total_views = sum(quote.views for quote in Quote.objects.all())
    total_likes = sum(quote.likes for quote in Quote.objects.all())
    
    # Самые популярные источники
    popular_sources = Source.objects.annotate(
        total_quotes=models.models.Count('quote'),
        total_likes=models.Sum('quote__likes')
    ).order_by('-total_likes')[:5]
    
    # Фильтрация
    source_type = request.GET.get('type', '')
    min_likes = request.GET.get('min_likes', 0)
    
    filtered_quotes = Quote.objects.all()
    
    if source_type:
        filtered_quotes = filtered_quotes.filter(source__type=source_type)
    
    if min_likes:
        filtered_quotes = filtered_quotes.filter(likes__gte=int(min_likes))
    
    filtered_quotes = filtered_quotes.order_by('-likes')[:20]
    
    context = {
        'total_quotes': total_quotes,
        'total_sources': total_sources,
        'total_views': total_views,
        'total_likes': total_likes,
        'popular_sources': popular_sources,
        'filtered_quotes': filtered_quotes,
        'source_type': source_type,
        'min_likes': min_likes,
    }
    
    return render(request, 'dashboard.html', context)"""

def edit_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    
    if request.method == 'POST':
        weight = int(request.POST.get('weight', 1))
        quote.weight = weight
        quote.save()
        messages.success(request, 'Вес цитаты обновлен!')
        return redirect('dashboard')
    
    return render(request, 'edit_quote.html', {'quote': quote})