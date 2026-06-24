from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
 
from .forms import RegistrationForm, OTPForm, LoginForm
from .models import User, OTPVerification


def send_otp_email(user, otp):
    # rn email is in the terminal, will change later

    subject = "CampusVote - Your verification code"
    message = (
        f"Hi {user.first_name}, \n \n"
        f"Your CampusVote verification code is {otp.code}\n"
        f"If you didnt request this, then lite lo."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False

    )




def register_view(request):
    if request.user.is_authenticated and request.user.is_verified:
        return redirect("vote")
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            otp = OTPVerification.generate_for(user)

            try:
                send_otp_email(user, otp)
            except Exception:
                messages.warning(request, "Account created but we couldn't send the OTP email. Use 'Resend OTP' on the next page.")

            request.session["pending_user_id"] = user.id
            messages.success(request, "Account created! Check your email for the OTP.")
            return redirect("verify_otp")
        
    else:
            form = RegistrationForm()
        
    return render(request, "accounts/register.html", {"form" : form})


def verify_otp_view(request):
    # case test
    user = None
    if request.user.is_authenticated:
        user = request.user
    elif "pending_user_id" in request.session:
        user = User.objects.filter(id=request.session["pending_user_id"]).first()
 
    # No user to verify
    if user is None:
        messages.error(request, "Please register or log in first.")
        return redirect("register")
 
    # Already verified
    if user.is_verified:
        return redirect("vote")
 
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            otp = OTPVerification.objects.filter(user=user).first()
 
            if otp is None:
                messages.error(request, "No OTP found. Please request a new one.")
            elif otp.is_expired():
                messages.error(request, "OTP expired. Please request a new one.")
            elif otp.code != entered_code:
                messages.error(request, "Incorrect OTP. Please try again.")
            else:
                user.is_verified = True
                user.save()
                otp.delete()
                request.session.pop("pending_user_id", None)
                login(request, user)
                messages.success(request, "Email verified successfully!")
                return redirect("vote")
    else:
        form = OTPForm()
 
    return render(request, "accounts/verify_otp.html", {"form": form, "user_email": user.email})



def resend_otp_view(request):
    user = None
    if request.user.is_authenticated:
        user = request.user
    elif "pending_user_id" in request.session:
        user = User.objects.filter(id=request.session["pending_user_id"]).first()

    if user is None or user.is_verified:
        return redirect("register")
    
    otp = OTPVerification.generate_for(user)
    send_otp_email(user, otp)

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_otp")



def login_view(request):
    if request.user.is_authenticated and request.user.is_verified:
        return redirect("vote")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            password = form.cleaned_data["password"]
 
            # username is email
            user = authenticate(request, username=email, password=password)
 
            if user is None:
                messages.error(request, "Invalid email or password.")
            else:
                login(request, user)
 
                if not user.is_verified:
                    messages.info(request, "Please verify your email to continue.")
                    return redirect("verify_otp")
 
                return redirect("vote")
    else:
        form = LoginForm()
 
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """Logs the user out and redirects to login page."""
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")



    


            


