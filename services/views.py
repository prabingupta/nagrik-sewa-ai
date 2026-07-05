import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .ai_engine import get_service_guidance
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import NagarikRegistrationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .models import Service, Query, Favorite


@login_required
def history(request):
    """Displays the most recent questions asked, newest first."""
    queries = Query.objects.select_related("service").order_by("-created_at")[:50]
    return render(request, "services/history.html", {
        "queries": queries,
    })


def register_view(request):
    """Simple registration using Django's built-in UserCreationForm."""
    if request.user.is_authenticated:
        return redirect("services:home")

    if request.method == "POST":
        form = NagarikRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("services:home")
    else:
        form = NagarikRegistrationForm()

    return render(request, "services/register.html", {"form": form})


class NagarikLoginView(LoginView):
    template_name = "services/login.html"
    redirect_authenticated_user = True


from django.contrib.auth import logout as auth_logout


def logout_view(request):
    """Logs the user out via a simple GET request and redirects home."""
    auth_logout(request)
    return redirect("services:home")


@login_required
def my_favorites(request):
    """Shows the current user's bookmarked services."""
    favorites = Favorite.objects.filter(user=request.user).select_related("service")
    return render(request, "services/favorites.html", {
        "favorites": favorites,
    })


@login_required
@require_POST
def toggle_favorite(request, service_id):
    """Toggle a service as favorited/unfavorited for the current user. Returns JSON."""
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return JsonResponse({"error": "Service not found"}, status=404)

    favorite, created = Favorite.objects.get_or_create(user=request.user, service=service)
    if not created:
        favorite.delete()
        return JsonResponse({"favorited": False})

    return JsonResponse({"favorited": True})


@login_required
def home(request):
    """Homepage: hero section + popular services."""
    popular_services = Service.objects.filter(is_popular=True)

    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(
            Favorite.objects.filter(user=request.user).values_list("service_id", flat=True)
        )

    return render(request, "services/home.html", {
        "popular_services": popular_services,
        "favorited_ids": favorited_ids,
    })


@csrf_exempt
@require_http_methods(["POST"])
def ask_query(request):
    """
    Receives a user question (JSON: {"question": "...", "language": "en"}),
    and returns a structured AI-generated answer. Requires login.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required", "login_required": True}, status=401)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    question = body.get("question", "").strip()
    language = body.get("language", "en")

    if not question:
        return JsonResponse({"error": "Question is required"}, status=400)

    answer = get_service_guidance(question, language)

    Query.objects.create(
        question=question,
        answer_json=answer,
        language=language,
    )

    return JsonResponse({"answer": answer})
