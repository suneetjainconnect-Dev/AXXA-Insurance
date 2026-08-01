from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create customer profile
            from .models import Customer
            Customer.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'insurance/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('insurance:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'insurance/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('insurance:index')
