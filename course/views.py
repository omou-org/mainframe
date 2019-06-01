from django.http import JsonResponse

from course.models import Course


def get_catalog(request):
	course_catalog = list(Course.objects.all())
	return JsonResponse({
		"data": course_catalog
	})
