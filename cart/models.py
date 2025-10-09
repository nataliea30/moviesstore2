from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=2, default="CA")  # <-- new field

    def __str__(self):
        return str(self.id) + ' - ' + self.user.username
    
    def save(self, *args, **kwargs):
        if self.user and hasattr(self.user, "userprofile"):
            self.state = self.user.userprofile.state
        super().save(*args, **kwargs)

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name