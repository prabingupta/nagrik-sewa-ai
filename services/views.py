import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Service, Query


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
    and returns a structured answer.

    For now this returns a placeholder — Phase 3 will replace this
    with a real AI call.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    question = body.get("question", "").strip()
    language = body.get("language", "en")

    if not question:
        return JsonResponse({"error": "Question is required"}, status=400)

    # --- Placeholder structured answer (replaced by AI in Phase 3) ---
    answer = {
        "service_name": "Passport Application",
        "steps": [
            "Fill the online passport application form (nepalpassport.gov.np)",
            "Book an appointment date at your nearest District Administration Office",
            "Visit the office on your appointment date with required documents",
            "Submit biometric details (photo, fingerprints)",
            "Pay the passport fee",
            "Collect passport on the notified date",
        ],
        "documents": [
            "Citizenship certificate (original + copy)",
            "Old passport (if renewing)",
            "Passport-size photo (as per specification)",
        ],
        "cost": "NPR 5,000 (normal, 34 pages) / NPR 12,000 (fast track)",
        "office": "District Administration Office or Department of Passports, Kathmandu",
        "tips": [
            "Book your appointment slot early — slots fill up fast.",
            "Double-check your citizenship certificate details before applying.",
        ],
    }

    # Save to database for history/logging
    Query.objects.create(
        question=question,
        answer_json=answer,
        language=language,
    )

    return JsonResponse({"answer": answer})