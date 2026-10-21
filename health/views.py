from django.http import JsonResponse


def health_check(request):
    # Return a simple JSON response to confirm that the backend can respond.
    return JsonResponse({"status": "ok"})