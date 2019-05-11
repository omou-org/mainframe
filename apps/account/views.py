from django.http import HttpResponse


def index(request):
    return HttpResponse("Account index page.")