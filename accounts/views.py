from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            
            username = email.split('@')[0]

            user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'Registration successful. You can now log in.')
                # ✅ Redirect after success
            return redirect('register')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    return render(request, 'accounts/login.html')


def logout(request):
    return redirect('store')
