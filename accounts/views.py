from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import UserProfile
import random
import datetime
from django.utils import timezone
import requests


def login(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']

        try:
            url = "http://webapp.webhop.net:8399/api/login/SupplierLoginToken"
            response = requests.post(url=url, data={'vendorCode': username, 'pin': password})
            token = response.json()
            # print(token)
            if(token==2):
                messages.info(request, "Invalid Credentials")
                return redirect("login")
            else:
                messages.info(request, "")
                response1 = redirect("dashboard")
                response1.set_cookie('token', token)
                return response1

        except Exception as e:
            messages.info(request, e)
            return redirect("login")

    else:
        messages.info(request, "")
        return render(request, 'auth/login.html')


def dashboard(request):
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
        token = request.COOKIES['token']
        headers = {"Authorization": f"Bearer {token}"}
        url = "http://webapp.webhop.net:8399/api/SupplierPortalApi/getcompanylist"
        response = requests.get(url=url, headers=headers)
        companylist = response.json()['data']
        return render(request, 'index.html', {'data': companylist})




# Code Needed to be Changed Later -> API Integration

def reset_password1(request):
    if(request.method == 'POST'):
        loginId = request.POST['LoginId']

        try:
            url = f"http://webapp.webhop.net:8399/api/login/gettemppass?LoginId={loginId}"
            response = requests.post(url=url)
            # print(response.json())

            messages.info(request, "Email Sent Successfully, Check your Mail Box !!")
            return render(request, 'auth/login.html')

        except Exception as e:
            messages.info(request, "Something Went Wrong !!")
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


