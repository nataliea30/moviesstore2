from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Petition, Vote
from .forms import PetitionForm

def index(request):
    """Display all petitions with vote counts"""
    petitions = Petition.objects.annotate(
        yes_count=Count('votes', filter=Q(votes__vote_type='yes')),
        no_count=Count('votes', filter=Q(votes__vote_type='no'))
    ).order_by('-created_at')
    
    context = {
        'template_data': {'title': 'Movie Petitions'},
        'petitions': petitions,
    }
    return render(request, 'petitions/index.html', context)

@login_required
def create(request):
    """Create a new petition"""
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.created_by = request.user
            petition.save()
            messages.success(request, 'Petition created successfully!')
            return redirect('petitions.index')
    else:
        form = PetitionForm()
    
    context = {
        'template_data': {'title': 'Create Petition'},
        'form': form,
    }
    return render(request, 'petitions/create.html', context)

@login_required
@require_POST
def vote(request, petition_id):
    """Vote on a petition"""
    petition = get_object_or_404(Petition, id=petition_id)
    vote_type = request.POST.get('vote_type')
    
    if vote_type not in ['yes', 'no']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    # Check if user already voted
    existing_vote = Vote.objects.filter(petition=petition, user=request.user).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.vote_type = vote_type
        existing_vote.save()
        message = f'Your vote has been updated to {vote_type}'
    else:
        # Create new vote
        Vote.objects.create(petition=petition, user=request.user, vote_type=vote_type)
        message = f'Your vote ({vote_type}) has been recorded'
    
    # Get updated vote counts
    yes_count = petition.yes_votes_count
    no_count = petition.no_votes_count
    total_count = petition.total_votes_count
    
    return JsonResponse({
        'success': True,
        'message': message,
        'yes_count': yes_count,
        'no_count': no_count,
        'total_count': total_count,
        'user_vote': vote_type
    })

def detail(request, petition_id):
    """View petition details"""
    petition = get_object_or_404(Petition, id=petition_id)
    user_vote = None
    
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(petition=petition, user=request.user).first()
    
    context = {
        'template_data': {'title': f'Petition: {petition.title}'},
        'petition': petition,
        'user_vote': user_vote,
    }
    return render(request, 'petitions/detail.html', context)
