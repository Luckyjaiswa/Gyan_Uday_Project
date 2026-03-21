from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from .forms import LoginForm, UserUpdateForm
from .models import User


# ─────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────
def login_view(request):
    """
    Handles GET (show form) and POST (authenticate user).
    Redirects to dashboard on success, back to login on failure.
    Role-based redirect can be added here later (e.g. students → their portal).
    """
    # If already logged in, go straight to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            # Respect ?next= parameter (Django sets this automatically)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)

            # Role-based redirect
            if user.is_admin():
                return redirect('dashboard:home')
            elif user.is_faculty():
                return redirect('dashboard:home')
            else:
                return redirect('dashboard:home')
                # Phase 3+: redirect students to their own portal page
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'accounts/login.html', {'form': form})


# ─────────────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────────────
def logout_view(request):
    """
    Logs out the current user and redirects to the login page.
    Accepts both GET and POST for convenience during development.
    In production, restrict to POST only using a form with CSRF token.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ─────────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    """
    Shows the current user's profile.
    GET  → display profile details
    POST → update profile details
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# ─────────────────────────────────────────────────────────────────
# CHANGE PASSWORD
# ─────────────────────────────────────────────────────────────────
@login_required
def change_password_view(request):
    """
    Allows logged-in users to change their own password.
    Uses Django's built-in PasswordChangeForm which validates
    the old password before setting the new one.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    # Apply form-control class to all password fields
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'accounts/change_password.html', {'form': form})
