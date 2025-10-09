from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    movie_title = models.CharField(max_length=255, help_text="The title of the movie you want to petition for")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_petitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.movie_title}"
    
    @property
    def yes_votes_count(self):
        return self.votes.filter(vote_type='yes').count()
    
    @property
    def no_votes_count(self):
        return self.votes.filter(vote_type='no').count()
    
    @property
    def total_votes_count(self):
        return self.votes.count()

class Vote(models.Model):
    VOTE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petition_votes')
    vote_type = models.CharField(max_length=3, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('petition', 'user')  # Each user can only vote once per petition
    
    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on {self.petition.title}"