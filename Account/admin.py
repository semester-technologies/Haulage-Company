from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([CustomUser, Administrator, Company, Manager, Registrar, Driver, AssistantDriver, MaintenanceOfficer])