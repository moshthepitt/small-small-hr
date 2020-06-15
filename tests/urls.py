"""URLs for testing."""
from django.http import HttpResponse
from django.urls import include, path


def homeview(request):
    """Return home page."""
    return HttpResponse("<h1>home page</h1>")


urlpatterns = [
    path("", homeview),
    path("reviews/", include("model_reviews.urls")),
]
