from django import forms
from .models import Petition

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'description', 'movie_title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the movie title'
            }),
        }
        labels = {
            'title': 'Petition Title',
            'description': 'Description',
            'movie_title': 'Movie Title',
        }