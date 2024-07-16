from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import UserProfile
import random
import datetime
from django.utils import timezone

# Create your views here.

def login(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            user_profile = UserProfile.objects.filter(user=user).values()
            is_verified = user_profile[0]['is_verified']
            
            if(is_verified):
                print("Home Page")
                messages.info(request, "Success")
                return render(request, 'index.html')
            else:
                return redirect("reset_password")
        else:
            messages.info(request, "Invalid Credentials")
            return redirect("login")
        
    else:
        messages.info(request, "")
        return render(request, 'auth/login.html')


def reset_password1(request):
    if(request.method == 'POST'):
        email = request.POST['email']
        otp = random.randint(100000, 999999)
        user = User.objects.filter(email=email).values()
        
        try:
            user_profile = UserProfile.objects.get(user=user[0]['id'])
            user_profile.otp = otp
            time_change = datetime.timedelta(minutes=5) 
            user_profile.otp_expiry = datetime.datetime.now() + time_change
            user_profile.save()

            return render(request, 'auth/reset_password2.html', {'email': email})
        except Exception as e:
            messages.info(request, "Invalid Email Id")
            return render(request, 'auth/reset_password1.html')
        
    else:
        messages.info(request, "")
        return render(request, 'auth/reset_password1.html')

def reset_password2(request):
    if(request.method == 'POST'):
        email = request.POST['email']
        otp = request.POST['otp']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.info(request, "Password Must be Same")
            return render(request, 'auth/reset_password2.html', {'email': email})
        else:
            user = User.objects.filter(email=email).values()
            user_profile = UserProfile.objects.get(user=user[0]['id'])
            # print("OTP: ", otp, type(otp), user_profile.otp, type(user_profile.otp))
            if(user_profile.otp == int(otp)):
                if user_profile.otp_expiry > timezone.now():
                    user1 = User.objects.get(email=email)
                    user1.set_password(password)
                    user1.save()
                    user_profile.is_verified = True
                    user_profile.save()
                    messages.info(request, "Success")
                    return redirect('login')
                else:
                    messages.info(request, "OTP Expired !!")
                    return render(request, 'auth/reset_password2.html', {'email': email})
            else:
                messages.info(request, "Invalid OTP !!")
                return render(request, 'auth/reset_password2.html', {'email': email})
            
    else:
        messages.info(request, "")
        return render(request, 'auth/reset_password2.html')


def change_password(request):
    if(request.method == 'POST'):
        email = request.POST['email']
        old_password = request.POST['old_password']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.info(request, "Password Must be Same")
            return render(request, 'auth/change_password.html', {'email': email})
        else:
            username = User.objects.get(email=email)
            user = auth.authenticate(username=username.username, password=old_password)
            print(user)
            if user is not None:
                user1 = User.objects.get(email=email)
                user1.set_password(password)
                user1.save()
                messages.info(request, "Success")
                return redirect('login')
            else:
                messages.info(request, "Invalid Credentials")
                return render(request, 'auth/change_password.html', {'email': email})
            
    else:
        messages.info(request, "")
        return render(request, 'auth/change_password.html')