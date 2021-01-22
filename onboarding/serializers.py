from rest_framework import serializers
from .onboarding import Upload

class UploadSerializer(serializers.Serializer):
    upload_file = serializers.FileField()

    def create(self, validated_data):
        print("inside create method")
        print("datazz: ", validated_data)
        return Upload(**validated_data)

def process_uploads():
# error = False

    upload_order = ["course_categories", "instructor", "course", "student", "parent"]
    print("hello")

    sheet = load_workbook(import_sheets.student).active
    for row in range(2, sheet.max_row + 1):
        for col in range(1, sheet.max_column + 1):
            print(sheet.cell(row=row, column=col).value)


def file_name_checker(ar):
    corrects = [False] * 5
    for i, f in enumerate(ar):
        if f in import_sheets.values():
            corrects[i] = True
    return [ar[i] for i in corrects if i == False]