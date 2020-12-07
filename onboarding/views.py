from django.shortcuts import render
from django.http import HttpResponse

from openpyxl import load_workbook
from course.models import Course, CourseCategory

import_sheets = {
    "student" : "students.xlsx",
    "parent" : "parents.xlsx",
    "course" : "course.xlsx",
    "instructor" : "instructors.xlsx",
    "course_categories" : "course_categories.xlsx"
}

def upload(request):
    # error = False

    upload_order = ["course_categories", "instructor", "course", "student", "parent"]

    for c in CourseCategory.objects.all():
        print(c)
    
    sheet = load_workbook(import_sheets.student).active
    for row in range(2, sheet.max_row + 1):
        for col in range(1, sheet.max_column + 1):
            print(sheet.cell(row=row, column=col).value)


    # if error:
    #     return HttpResponse("error")
    # else:
    #     return HttpResponse("success")

def file_name_checker(ar):
    corrects = [False] * 5
    for i, f in enumerate(ar):
        if f in import_sheets.values():
            corrects[i] = True
    return [ar[i] for i in corrects if i == False]