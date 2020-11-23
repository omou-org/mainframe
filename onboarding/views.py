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

from openpyxl import load_workbook
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class FileUpload(APIView):
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        print("data", request.data)
        # upload_file = Upload(upload_file = request.data["upload_file"])
        serializer = UploadSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer["upload_file"])
            path = default_storage.save('tmp/curr.xlsx', ContentFile(serializer["upload_file"]))
            # wb = load_workbook(filename=serializer["upload_file"])
            # print(wb)
            
            # f = serializer.save(serializer["upload_file"])
            # print(f)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return HttpResponse("failed")


import_sheets = {
    "student" : "students.xlsx",
    "parent" : "parents.xlsx",
    "course" : "course.xlsx",
    "instructor" : "instructors.xlsx",
    "course_categories" : "course_categories.xlsx"
}


