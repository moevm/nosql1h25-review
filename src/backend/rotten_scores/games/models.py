from django.db import models

# Create your models here.
class Game(models.Model):
    title = models.CharField(max_length=255, db_index=True)  # индекс по названию
    cover_url = models.URLField(null=True, blank=True)       # ссылка на обложку
    release_date = models.DateField(null=True, blank=True)   # дата выхода
    critic_score = models.FloatField(null=True, blank=True)  # средняя оценка критиков

    def __str__(self):
        return self.title