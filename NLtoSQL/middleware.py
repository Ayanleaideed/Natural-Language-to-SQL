from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL patterns that don't require authentication
        auth_path = [
            reverse('login_user'),
            reverse('register'),
            reverse('demoLogin')
        ]

        if not request.user.is_authenticated and request.path not in auth_path:
            return redirect(settings.LOGIN_URL)

        response = self.get_response(request)
        return response
