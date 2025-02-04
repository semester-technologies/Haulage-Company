from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from Wallet.models import Wallet

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import secrets
import string

from django.core.mail import send_mail
from django.conf import settings



# Create your views here.


def generate_referral_code(length=8):
    while True:
        code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        if not CustomUser.objects.filter(referral_code=code).exists():
            return code



def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        referral_code = request.POST.get('referral_code')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check for existing username
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
            return redirect('register-user')

        # Check for existing email
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already taken.")
            return redirect('register-user')

        # Check password match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register-user')

        # Validate referral code
        referrer = None
        if referral_code:
            try:
                referrer = CustomUser.objects.get(referral_code=referral_code)
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid referral code.")
                return redirect('register-user')
        
        try:
            # Create the User
            user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1
            )
            user.referral_code = generate_referral_code()
            user.save()

    
            if referrer:
                referrer.my_referrals.add(user)
                user.referred_by = referrer
                user.save()
                print(f"Referred by: {referrer.username}")


            messages.success(request, "You have successfully registered!")
            return redirect('login-user')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'register.html')
    return render(request, 'register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in successfully")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login-user')
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('login-user')


@login_required(login_url='login/')
def dashboard(request):
    """ Display stats of the system """
    user_account_status = request.user.is_approved
    context = {
        'user_account_status': user_account_status
    }
    return render(request, 'dashboard.html', context)




def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)

            # Generate reset link (use token generator for security)
            reset_link = f"http://127.0.0.1:8000/reset-password/{user.id}/"

            # Send the email
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('password_reset_request')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with this email address.')

    return render(request, 'password_reset_request.html')





def password_reset_confirm(request, user_id):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid user.')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'password_reset_confirm.html')



















@login_required(login_url='/login/')
def user_profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')

        user = request.user  # Get the logged-in user

        # Update user details
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.save()

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('update-profile')

    return render(request, 'update-profile.html')




@login_required
def referral_list(request):
    """List all referrals of the current user."""
    referrals = request.user.my_referrals.all()
    return render(request, 'referral-list.html', {'referrals': referrals})

@login_required
def pending_approvals(request):
    """List all users waiting for approval by the current user."""
    pending_referrals = CustomUser.objects.filter(
        referral_owner=request.user, is_approved=False
    )
    return render(request, 'pending-approvals.html', {'pending_referrals': pending_referrals})


@login_required
def referral_detail(request, user_id):
    """View details of a user waiting for approval."""
    referral_user = get_object_or_404(CustomUser, id=user_id, referral_owner=request.user)
    return render(request, 'referral-detail.html', {'referral_user': referral_user})



@login_required
def approve_referral(request, user_id):
    """Approve a referral."""
    referral_user = get_object_or_404(CustomUser, id=user_id, referral_owner=request.user)
    referral_user.is_approved = True
    referral_user.save()

    # Create a unique wallet for the user
    Wallet.objects.get_or_create(user=referral_user)

    return redirect('pending-approvals')


@login_required
def reject_referral(request, user_id):
    """Reject a referral."""
    referral_user = get_object_or_404(CustomUser, id=user_id, referral_owner=request.user)
    referral_user.my_referrals.remove(request.user)
    referral_user.save()
    return redirect('pending-approvals')


@login_required
def submit_kyc(request):
    """Submit KYC documents."""
    if request.method == 'POST':
        address = request.POST.get('address')

        nin_picture = request.POST.get('nin_picture')
        nin_number = request.POST.get('nin_number')
        address = request.POST.get('address')
        referred_by_username = request.POST.get('referred_by')

        try:
            user = request.user
            referred_by_user = CustomUser.objects.get(username=referred_by_username)

            # Save KYC documents to the database
            kyc = KYC.objects.create(
                user=user,
                address=address,
                nin_picture=nin_picture,
                nin_number=nin_number,
                referred_by=referred_by_user
            )
            messages.success(request, 'KYC documents submitted successfully.')
            return redirect('dashboard')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid referral username.')
            return redirect('submit-kyc')
        except Exception as e:
            messages.error(request, 'Error submitting KYC documents: ' + str(e))
            return redirect('submit-kyc')
    else:
        user = request.user
        if user.referred_by:
            return render(request, 'kyc.html', {'referred_by': user.referred_by.username})
        else:
            return render(request, 'kyc.html')

