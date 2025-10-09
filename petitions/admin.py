from django.contrib import admin
from .models import Petition, Vote

@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'movie_title', 'created_by', 'created_at', 'yes_votes_count', 'no_votes_count', 'total_votes_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('title', 'movie_title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'petition', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__username', 'petition_title')