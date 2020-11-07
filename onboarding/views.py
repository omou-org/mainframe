from django.shortcuts import render
from django.http import HttpResponse

from openpyxl import load_workbook
from course.models import Course, CourseCategory
from graphene_django.views import GraphQLView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadSerializer
# from rest_framework import MultiPartParser
from .onboarding import Upload

class FileUpload(APIView):
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        upload_file = Upload(upload = request.data["upload"])
        print("data", request.data)
        serializer = UploadSerializer(upload_file)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return HttpResponse("failed")


import_sheets = {
    "student" : "students.xlsx",
    "parent" : "parents.xlsx",
    "course" : "course.xlsx",
    "instructor" : "instructors.xlsx",
    "course_categories" : "course_categories.xlsx"
}


