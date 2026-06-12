from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegistrationForm(forms.ModelForm):
    # Validates onnly bits domain
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "password"}),
        label = "Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "password"}),
        label = "Confirm password"
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "hostel", "room_number"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "yourname@pilani.bits-pilani.ac.in"}),
            "hostel": forms.TextInput(attrs={"placeholder": "Hostel Name"}),
            "room_number": forms.TextInput(attrs={"placeholder": "Room Number"}),
        }

    def clean_email(self):
        # rules for email registration n shi

        email = self.cleaned_data["email"].lower().strip()

        allowed = settings.ALLOWED_EMAIL_DOMAINS

        if not any(email.endswith("@" + domain) for domain in allowed):
            raise forms.ValidationError(
                f"Only college emails are allowed (eg @{allowed[0]})"
            )
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email is already registered.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    

    def save(self, commit = True):
        # user is saved w email but username is reqd for abstractuser
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password"])
        user.is_verified = False
        if commit:
            user.save()
        return user
    

class OTPForm(forms.Form):
    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            "placeholder" : "Enter 4 digit OTP",
            "autocomplete" : "one-time-code",
            "inputmode" : "numeric"
        }),
        label="OTP code"
    )

class LoginForm(forms.Form):

    email = forms.EmailField(
        widget= forms.EmailInput(attrs= {"placeholder" : "yourID@pilani.bits-pilani.ac.in"}),
        label = "Email"
    )

    password = forms.CharField(
        widget= forms.PasswordInput(attrs={"placeholder": "Password"}),
        label = "password"
    )




