import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .ai_engine import get_service_guidance
from .models import Service, Query


def history(request):
    """Displays the most recent questions asked, newest first."""
    queries = Query.objects.select_related("service").order_by("-created_at")[:50]
    return render(request, "services/history.html", {
        "queries": queries,
    })


def home(request):
    """Homepage: hero section + popular services."""
    popular_services = Service.objects.filter(is_popular=True)
    return render(request, "services/home.html", {
        "popular_services": popular_services,
    })


@csrf_exempt
@require_http_methods(["POST"])
def ask_query(request):
    """
    Receives a user question (JSON: {"question": "...", "language": "en"}),
    and returns a structured AI-generated answer.
    """
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
