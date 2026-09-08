from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from . import forms
from .services import can_view_profile, get_user_stats
from games.models import CollectionEntry
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method =='POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my-collection')
    else:
        form = forms.RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def my_collection(request):
    user = request.user
    collection = CollectionEntry.objects.filter(user=user).select_related('game')
    return render(request, 'accounts/my_collection.html', {'collection': collection})

def profile_detail(request, username):
    User = get_user_model()
    profile_owner = get_object_or_404(User, username=username)
    can_view = can_view_profile(request.user, profile_owner)

    context = {'profile_owner': profile_owner, 'can_view': can_view}
    if can_view:
        context['stats'] = get_user_stats(profile_owner)

    return render(request, 'accounts/profile_detail.html', context)