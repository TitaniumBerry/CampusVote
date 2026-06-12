# redirect unverified users to login

from django.shortcuts import redirect


class VerifyOTPMiddleware:
    # urls that unverified user is allowed ro access

    ALLOWED_URL_NAMES = {
        "verify_otp",
        "resend_otp",
        "logout"
    }

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user

        if user.is_authenticated and user.is_staff:
            return self.get_response(request)

 
        if user.is_authenticated and not user.is_verified:
            # idk how this works
            url_name = getattr(request.resolver_match, "url_name", None)
 
            if url_name not in self.ALLOWED_URL_NAMES:
                return redirect("verify_otp")
 
        return self.get_response(request)
 

