from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        # email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, password, **extra_fields)


USER_LEVEL = [
    (1, 'Level 1'),
    (2, 'Level 2'),
    (3, 'Level 3'),
    ]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField()
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=50, blank=True, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to="User Profile Image", blank=True, null=True)
    referral_code = models.CharField(max_length=255, blank=True, null=True, unique=True)      
    level = models.IntegerField(choices=USER_LEVEL, default=1)
    is_approved = models.BooleanField(default=False)
    referred_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    my_referrals = models.ManyToManyField('self', symmetrical=False, related_name="referral_owner", blank=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)
    is_loan_eligible = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'



class KYC(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nin_picture = models.ImageField(upload_to='kyc_nin/')
    nin_number = models.IntegerField( blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    date_submitted = models.DateTimeField(auto_now_add=True)
    referred_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="kyc_referred_by")
    is_approved = models.BooleanField(default=False)
    
    def approve_kyc(self):
        self.status = 'approved'
        self.save()

    def __str__(self):
        return self.user.username
    


class MonthlyDue(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=[
        ('jan', 'Jan'), 
        ('feb', 'Feb'), 
        ('mar', 'Mar'), 
        ('apr', 'Apr'), 
        ('may', 'May'), 
        ('jun', 'Jun'), 
        ('jul', 'Jul'), 
        ('aug', 'Aug'), 
        ('sep', 'Sep'), 
        ('oct', 'Oct'),
        ('nov', 'Nov'),
        ('dec', 'Dec'),
        ], default='jan')
    
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    date = models.DateField(default=timezone.now)
    
    def calculate_due(self):
        # Adjust based on user level
        if self.user.level == 1:
            self.amount_due = 5000  # Example amount for Level 1
        elif self.user.level == 2:
            self.amount_due = 10000  # Example amount for Level 2
        elif self.user.level == 3:
            self.amount_due = 15000  # Example amount for Level 3
        self.save()