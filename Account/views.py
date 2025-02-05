from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import secrets
import string

from django.core.mail import send_mail
from django.conf import settings



# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('login-user')

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']
        user = CustomUser.objects.create_user(email=email, password=password)
        Administrator.objects.create(user=user, full_name=full_name)
        messages.success(request, 'Account created successfully. Please login.')
        return redirect('login-user')
    return render(request, 'register.html')














def company_list(request):
    companies = Company.objects.filter(owner__user=request.user)
    return render(request, 'companies/list.html', {'companies': companies})

def company_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        admin = Administrator.objects.get(user=request.user)
        Company.objects.create(name=name, owner=admin)
        return redirect('company_list')
    return render(request, 'companies/create.html')

def company_delete(request, company_id):
    company = get_object_or_404(Company, id=company_id, owner__user=request.user)
    company.delete()
    return redirect('company_list')

# Views for Employee Management
def employee_list(request, company_id):
    company = get_object_or_404(Company, id=company_id, owner__user=request.user)
    employees = Employee.objects.filter(company=company)
    return render(request, 'employees/list.html', {'employees': employees, 'company': company})

def employee_create(request, company_id):
    company = get_object_or_404(Company, id=company_id, owner__user=request.user)
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        user = CustomUser.objects.create_user(email=email, password=password)
        employee_model = globals().get(role)
        if employee_model:
            employee_model.objects.create(user=user, company=company, full_name=full_name)
        return redirect('employee_list', company_id=company.id)
    return render(request, 'employees/create.html', {'company': company})

def employee_delete(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id, company__owner__user=request.user)
    employee.user.delete()
    employee.delete()
    return redirect('employee_list', company_id=employee.company.id)
