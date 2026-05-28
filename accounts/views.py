"""
accounts/views.py - User authentication views.

Handles:
  - GET/POST /register/  → RegisterView
  - GET/POST /login/     → LoginView
  - POST     /logout/    → LogoutView
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user in automatically
            login(request, user)
            messages.success(
                request,
                f"Welcome, {user.username}! Your account has been created successfully.",
            )
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                # Redirect to the page the user originally tried to visit
                next_url = request.GET.get("next", "dashboard")
                return redirect(next_url)
        messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """Log out the current user."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect("login")