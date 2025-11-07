from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidate, VotingResult
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from voting_app.models import CustomUser, UserData
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models import Count
from django.conf import settings
import os
def admin_login(request):
    """Admin login view."""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if User.objects.filter(username=username, is_superuser=1).exists():
            login(request, user)
            return redirect(admin_dashboard)
        else:
            messages.error(request, 'Invalid credentials or you are not an admin!')
            return redirect('admin_login')
    return render(request, 'admin_panel/admin_login.html')


def admin_logout(request):
    """Logout for admin."""
    logout(request)
    return redirect('admin_login')


@login_required
def admin_dashboard(request):
    return render(request, 'admin_panel/admin_dashboard.html')


def add_candidate(request):
    if request.method == 'POST':
        # Get the candidate data from the POST request
        candidate_id = request.POST.get('candidate_id')
        full_name = request.POST.get('full_name')
        party_name = request.POST.get('party_name')
        party_symbol = request.FILES.get('party_symbol')
        bio = request.POST.get('bio')

        # Validate if the candidate symbol file exists
        if not party_symbol:
            messages.error(request, 'Please upload a party symbol image.')
            return redirect('add_candidate')

        # Save the party symbol to the server (you can also check the file type here)
        file_name = default_storage.save(os.path.join('party_symbols', party_symbol.name), party_symbol)

        # Create and save the candidate instance
        try:
            candidate = Candidate(
                full_name=full_name,
                party_name=party_name,
                party_symbol=file_name,
                bio=bio
            )
            candidate.save()

            messages.success(request, 'Candidate added successfully!')
            return redirect('admin_dashboard')  # Redirect to the admin dashboard or another page after success
        except ValidationError as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'admin_panel/add_candidate.html')

@login_required
def view_candidates(request):
    candidates = Candidate.objects.all()
    return render(request, 'admin_panel/view_candidates.html', {'candidates': candidates})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Candidate


def edit_candidate(request, candidate_id):
    # Get the candidate by ID
    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Handle form submission logic for editing (for example, POST request)
    if request.method == "POST":
        # Update candidate details based on the form data
        candidate.full_name = request.POST['full_name']
        candidate.party_name = request.POST['party_name']
        candidate.party_symbol = request.FILES['party_symbol']  # If you're uploading an image
        candidate.bio = request.POST['bio']
        candidate.save()
        return redirect('view_candidates')  # Redirect to view candidates page after saving changes

    # If it's a GET request, render the form with current candidate data
    return render(request, 'admin_panel/edit_candidate.html', {'candidate': candidate})


def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    return redirect('view_candidates')

def view_voters(request):
    # Fetch voters excluding admin users (is_staff=False or not in Admin group)
    users = User.objects.filter(is_staff=False)  # Only non-admin users
    custom_users = UserData.objects.filter(user__in=users)  # Assuming CustomUser has a foreign key to User
    print(custom_users)
    context = {
        'users': users,
        'custom_users': custom_users,
    }
    return render(request, 'admin_panel/view_voters.html', context)


def view_votes(request):
    # Annotate each candidate with their vote count
    candidates = Candidate.objects.annotate(vote_count=Count('votingresult')).order_by('-vote_count')

    # Find the candidate with the most votes
    most_voted_candidate = candidates.first() if candidates else None

    context = {
        'candidates': candidates,
        'most_voted_candidate': most_voted_candidate
    }
    return render(request, 'admin_panel/view_vote.html', context)