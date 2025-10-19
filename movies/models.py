from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('movie', 'user')  # each user can rate a movie once

    def __str__(self):
        return f"{self.user.username} → {self.movie.name}: {self.value}"