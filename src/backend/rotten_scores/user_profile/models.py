from django.db import models
from core.models import User

class GameReview(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='userId'
    )
    title = models.CharField(max_length=255)
    cover_url = models.URLField(blank=True)
    rating = models.PositiveIntegerField()
    review = models.TextField()
    review_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"