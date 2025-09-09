from django.db import models

from django.core.exceptions import ValidationError

class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)
    type_choices = [
        ('movie', 'Фильм'),
        ('book', 'Книга'),
        ('other', 'Другое'),
    ]
    type = models.CharField(max_length=10, choices=type_choices)
    
    def __str__(self):
        return self.name

class Quote(models.Model):
    text = models.TextField(unique=True)  # запрещает дубликаты
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    weight = models.IntegerField(default=1)  # вес цитаты
    views = models.IntegerField(default=0)   # счетчик просмотров
    likes = models.IntegerField(default=0)   # лайки
    dislikes = models.IntegerField(default=0) # дизлайки
    
    def clean(self):
        # Проверяем, что у источника не больше 3 цитат
        if Quote.objects.filter(source=self.source).count() >= 3:
            raise ValidationError('У одного источника не может быть больше 3 цитат')
    
    def __str__(self):
        return f'"{self.text[:50]}..." from {self.source}'