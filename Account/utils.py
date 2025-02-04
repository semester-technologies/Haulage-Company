from django.core.mail import send_mail, get_connection
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
import json
from .models import *
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import datetime
from django.utils import timezone


def verify_email(request, uidb64, token):
    try:
        # Decode user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)

        # Get the token creation timestamp from the cookie
        token_created_at_cookie = request.COOKIES.get('token_created_at')

        # Check if the token creation timestamp exists in the cookie
        if token_created_at_cookie:
            token_created_at = datetime.datetime.strptime(token_created_at_cookie, '%Y-%m-%d %H:%M:%S.%f')
            if (timezone.now() - token_created_at).total_seconds() / 60 > 30:
                context = {
                    "status": "error",
                    "message": "Verification link has expired. Please request a new link."
                }
                return render(request, 'verification_result.html', context)

        # Validate the token
        if user and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            context = {
                "status": "success",
                "message": "Email successfully verified!"
            }
            return render(request, 'verification_result.html', context)
        else:
            context = {
                "status": "error",
                "message": "Invalid or expired verification link."
            }
            return render(request, 'verification_result.html', context)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        context = {
            "status": "error",
            "message": "Invalid verification link."
        }
        return render(request, 'verification_result.html', context)


def regenerate_verification_link(request, user):
    # Delete the existing verification token
    user.verification_token_created_at = None
    user.save()

    # Generate a new token and encoded user ID
    uid = urlsafe_base64_encode(force_bytes(user.email))
    token = default_token_generator.make_token(user)

    # Store the token creation timestamp
    user.verification_token_created_at = timezone.now()
    user.save()

    # Construct the verification link
    domain = get_current_site(request).domain if request else settings.SITE_DOMAIN
    verification_url = f"http://{domain}/api/verify-email/{uid}/{token}/"

    # Create the email payload for Loops
    payload = {
        "transactionalId": "cm5kwzpnu02gt57gt28advw85",
        "email": user.email,
        "dataVariables": {
            "email": user.email,
            "verification_url": verification_url,
        }
    }

    # Send the email
    with get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=True
    ) as connection:
        send_mail(
            subject="Verify Your Email",
            message=json.dumps(payload),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            connection=connection
        )

    context = {
        "status": "success",
        "message": "New verification link sent to your email."
    }
    return render(request, 'verification_result.html', context)


def resend_verification_email(request):
    try:
        user = request.user
        res = regenerate_verification_link(request, user)
        return res
    except Exception as e:
        context = {
            "status": "error",
            "message": str(e)
        }
        return render(request, 'verification_result.html', context)
