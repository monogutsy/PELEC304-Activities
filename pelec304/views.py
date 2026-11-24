from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def home(request):
    """Show the activity collection only to an authenticated superuser."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404
    return render(request, "home.html")
