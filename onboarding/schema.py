from onboarding.models import Business

from graphene import Field, ID, String
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required

from openpyxl import Workbook
from openpyxl.comments import Comment 
from tempfile import NamedTemporaryFile
import base64

class BusinessType(DjangoObjectType):
    class Meta:
        model = Business

class Query(object):
    business = Field(BusinessType, business_id=ID(), name=String())
    account_templates = String()

    @login_required
    @staff_member_required
    def resolve_business(self, info, **kwargs):
        business_id = kwargs.get('business_id')
        name = kwargs.get('name')

        if business_id:
            return Business.objects.get(id=business_id)

        if name:
            return Business.objects.get(name=name)

        return None

    
    def resolve_account_templates(self, info, **kwargs):
        wb = Workbook()
        wb.create_sheet("Parents.xlsx")
        wb.create_sheet("Students.xlsx")
        wb.create_sheet("Instructors.xlsx")

        # parent sheet
        parents_ws = wb.get_sheet_by_name("Parents.xlsx")
        parents_ws["A1"].comment = Comment(
            "Instructions: Please enter parent details in this spreadsheet similar to the example on row 3. Double check that all emails, phone numbers, and zip codes are valid, otherwise those parents may not be uploaded correctly.",
            "Omou Learning"
            )

        parents_column_names = ["First Name", "Last Name", "Email", "Phone", "Zip Code (Optional)"]
        parents_example = ["Ken", "Chan", "kennyken@yahoo.com",	"5635573354", "94345"]
        for c in range(len(parents_column_names)):
            parents_ws.cell(row=2, column=c+1).value = parents_column_names[c]
            parents_ws.cell(row=3, column=c+1).value = parents_example[c]

        # students
        students_ws = wb.get_sheet_by_name("Students.xlsx")
        students_ws["A1"].comment = Comment(
            "Instructions: Please enter student details in this spreadsheet similar to the example on row 3. Please enter the student's parent's first last name and email exactly as was entered in the parent spreadsheet, otherwise the student will not be visible under the parent's profile in Omou.",
            "Omou Learning"
            )

        students_column_names = ["First Name", "Last Name", "Email", "Birthday MM/DD/YYYY (Optional)", "School (Optional)", "Grade Level (Optional)", "Parent's First Name", "Parent's Last Name", "Parent's Email"]
        students_examples = ["Kevin", "Chan", "kev.chan@gmail.com", "08/08/2008", "Alamador High School", "11", "Ken", "Chan", "kennyken@yahoo.com"]
        for c in range(len(students_column_names)):
            students_ws.cell(row=2, column=c+1).value = students_column_names[c]
            students_ws.cell(row=3, column=c+1).value = students_examples[c]

        # instructors
        instructors_ws = wb.get_sheet_by_name("Instructors.xlsx")
        instructors_ws["A1"].comment = Comment(
            "Instructions: Please enter instructor details in this spreadsheet similar to the example on row 3. Instructors with invalid emails will not be entered into Omou, so please confirm the instructor's email is valid prior to submission!",
            "Omou Learning"
            )

        instructors_column_names = ["First Name", "Last Name", "Email", "Phone", "Biography (Optional)", "Years of Experience (Optional)", "Address (Optional)", "City", "State", "Zip Code"]
        instructors_examples = ["Vicky", "Lane", "vlane@gmail.com", "6453456765", "Vicky is experienced in teaching math for all skill levels.", "5", "456 Candy Lane", "Los Angeles", "CA", "90034"]
        for c in range(len(instructors_column_names)):
            instructors_ws.cell(row=2, column=c+1).value = instructors_column_names[c]
            instructors_ws.cell(row=3, column=c+1).value = instructors_examples[c]

        with NamedTemporaryFile() as tmp:
            wb.save(filename = tmp.name)
            tmp.seek(0)
            stream = tmp.read()   

        return base64.b64encode(stream)
