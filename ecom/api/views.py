from django.http import JsonResponse


def home(request):
    return JsonResponse({'name': 'Vinay', 'age': 32})
