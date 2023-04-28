from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login


# Create your views here.
def register(request):
    # redirect user if logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log in the user
            login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}! You are now logged in!')
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profilepage(request):
    return render(request, 'users/profile.html')
