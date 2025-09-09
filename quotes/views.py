from django.shortcuts import render, redirect
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
    return render(request, 'popular_quotes.html', {'quotes': quotes})