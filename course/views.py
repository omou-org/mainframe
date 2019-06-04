from django.http import JsonResponse

from course.models import Course


def get_catalog(request):
	courses = list(Course.objects.values())
	return JsonResponse({
		"data": courses,
	})
