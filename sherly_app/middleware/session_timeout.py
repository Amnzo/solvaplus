from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                idle_duration = timezone.now() - timezone.datetime.fromisoformat(last_activity)
                if idle_duration.total_seconds() > settings.SESSION_IDLE_TIMEOUT:
                    request.session.flush()  # Flush the session data
                    return redirect('bl_login')  # Redirect to your custom login view
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response
