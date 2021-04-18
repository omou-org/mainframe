from onboarding.models import Business

from graphene import Field, ID, String
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from tempfile import NamedTemporaryFile
import base64

from mainframe.permissions import IsOwner
from django_graphene_permissions import permissions_checker

from account.models import Instructor 


class BusinessType(DjangoObjectType):
    class Meta:
        model = Business


def workbook_to_base64(wb):
    with NamedTemporaryFile() as tmp:
        wb.save(filename = tmp.name)
        tmp.seek(0)
        stream = tmp.read()
    base64_stream = base64.b64encode(stream).decode("utf-8")
    return base64_stream


def create_accounts_template(show_errors=False):
    wb = Workbook()
    wb.create_sheet("Parents")
    wb.create_sheet("Students")
    wb.create_sheet("Instructors")

    # parent sheet
    parents_ws = wb.get_sheet_by_name("Parents")
    parents_ws["A1"].value = "Instructions: Please enter parent details in this spreadsheet similar to the example on row 3. Double check that all emails, phone numbers, and zip codes are valid, otherwise those parents may not be uploaded correctly."
    parents_ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    parents_ws["A1"].alignment = Alignment(wrapText=True)

    parents_column_names = ["First Name", "Last Name", "Email", "Phone", "Zip Code (Optional)"]
    if show_errors:
        parents_column_names.append("Error Message")
    parents_example = ["Ken", "Chan", "kennyken@yahoo.com",	"5635573354", "94345", ""]
    for c in range(len(parents_column_names)):
        parents_ws.cell(row=2, column=c+1).value = parents_column_names[c]
        parents_ws.cell(row=3, column=c+1).value = parents_example[c]

    # students
    students_ws = wb.get_sheet_by_name("Students")
    students_ws["A1"].value = "Instructions: Please enter student details in this spreadsheet similar to the example on row 3. Please enter the student's parent's first last name and email exactly as was entered in the parent spreadsheet, otherwise the student will not be visible under the parent's profile in Omou."
    students_ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    students_ws["A1"].alignment = Alignment(wrapText=True)

    students_column_names = ["First Name", "Last Name", "Email", "Birthday MM/DD/YYYY (Optional)", "School (Optional)", "Grade Level (Optional)", "Parent's First Name", "Parent's Last Name", "Parent's Email"]
    if show_errors:
        students_column_names.append("Error Message")
    students_example = ["Kevin", "Chan", "kev.chan@gmail.com", "08/08/2008", "Alamador High School", "11", "Ken", "Chan", "kennyken@yahoo.com", ""]
    for c in range(len(students_column_names)):
        students_ws.cell(row=2, column=c+1).value = students_column_names[c]
        students_ws.cell(row=3, column=c+1).value = students_example[c]

    # instructors
    instructors_ws = wb.get_sheet_by_name("Instructors")
    instructors_ws["A1"].value = "Instructions: Please enter instructor details in this spreadsheet similar to the example on row 3. Instructors with invalid emails will not be entered into Omou, so please confirm the instructor's email is valid prior to submission!"
    instructors_ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    instructors_ws["A1"].alignment = Alignment(wrapText=True)

    instructors_column_names = ["First Name", "Last Name", "Email", "Phone", "Biography (Optional)", "Years of Experience (Optional)", "Address (Optional)", "City", "State", "Zip Code"]
    if show_errors:
        instructors_column_names.append("Error Message")
    instructors_example = ["Vicky", "Lane", "vlane@gmail.com", "6453456765", "Vicky is experienced in teaching math for all skill levels.", "5", "456 Candy Lane", "Los Angeles", "CA", "90034", ""]
    for c in range(len(instructors_column_names)):
        instructors_ws.cell(row=2, column=c+1).value = instructors_column_names[c]
        instructors_ws.cell(row=3, column=c+1).value = instructors_example[c]

    # remove default sheet
    del wb['Sheet']

    # autosize columns
    for sheet_name in wb.sheetnames:
        sheet = wb.get_sheet_by_name(sheet_name)
        if sheet.sheet_state == 'hidden':
            continue
        autosize_ws_columns(sheet)
        # bold column headers
        for cell in sheet["2:2"]:
            cell.font = Font(bold=True)
        # increase comment row height
        sheet.row_dimensions[1].height=50
    
    return wb


# show_errors=True adds error message column
def create_course_templates(show_errors=False):
    wb = Workbook()
    wb.create_sheet("Instructor Roster (hidden)")
    wb.create_sheet("Step 1 - Subject Categories")
    wb.create_sheet("Step 2 - Classes")

    # instructors populate dropdown
    instructors_ws = wb.get_sheet_by_name("Instructor Roster (hidden)")
    instructors_ws.sheet_state = 'hidden'
    instructors_ws.cell(row=1, column=1).value = "Instructor Name (email)"
    for row, instructor in enumerate(Instructor.objects.all()):
        instructors_ws.cell(row=row+2, column=1).value = f"{instructor.user.first_name} {instructor.user.last_name} ({instructor.user.username})" 

    # subject categories
    categories_ws = wb.get_sheet_by_name("Step 1 - Subject Categories")
    categories_ws.cell(row=1, column=1).value = "Instructions: Please FIRST fill out the list of subject or course category in the first column. This will become a list of subjects to fill out the required course subject field in Step 2 - Classes sheet."
    
    categories_column_names = ["Subjects", "Description (Optional)"]
    if show_errors:
        categories_column_names.append("Error Message")
    categories_example = ["SAT Prep", "Preparational courses for students taking the SAT", ""]
    for c in range(len(categories_column_names)):
        categories_ws.cell(row=2, column=c+1).value = categories_column_names[c]
        categories_ws.cell(row=3, column=c+1).value = categories_example[c]

    # classes
    class_ws = wb.get_sheet_by_name("Step 2 - Classes")
    class_ws.cell(row=1, column=1).value = "Instructions: Please fill out the course details similar to the example in row 3. You may only select subjects previous defined in Step 1 - Subject Categories. You may only select instructors that are already in the database."
    class_ws.cell(row=1, column=10).value = 'Instructions: 5 course session slots are provided in format of "Session Day" "Start Time" and "End Time." "Session Day" is the day of week the session takes place on. If a course meets more than 5 times a week, please add additional "Session Day" "Start Time" and "End Time" columns in increasing order (e.g. "Session Day 6"). If a course only meets once, you may leave the other session slots empty.'

    class_column_names = ["Course Name", "Instructor", "Instructor Confirmed? (Y/N)", "Subject", "Course Description", "Academic Level", "Room Location", "Start Date",	"End Date", "Session Day 1", "Start Time 1", "End Time 1", "Session Day 2", "Start Time 2", "End Time 2", "Session Day 3", "Start Time 3", "End Time 3", "Session Day 4", "Start Time 4", "End Time 4", "Session Day 5", "Start Time 5", "End Time 5"]
    if show_errors:
        class_column_names.append("Error Message")
    for c in range(len(class_column_names)):
        class_ws.cell(row=2, column=c+1).value = class_column_names[c]
    
    class_example = ["SAT Math Prep", "Daniel Wong (email)", "Y", "SAT Prep", "This is a prep course for SAT math. Open for all grade levels.", "High School", "Online", "12/1/2021", "12/30/2021",	"Wednesday", "4:00 PM",	"5:00 PM", "Friday", "2:00 PM", "3:00 PM"]
    for c in range(len(class_example)):
        class_ws.cell(row=3, column=c+1).value = class_example[c]

    # academic level validation
    # academic_level_dv = DataValidation(type="list", formula1='$F:$F', allow_blank=False, showDropDown=True)
    # "Elementary,Middle_School,High_School,College"
    # class_ws.add_data_validation(academic_level_dv)
    # f3 to f infinity
    # instructor validation
    # subject validation

    # remove default sheet
    del wb['Sheet']

    # autosize columns
    for sheet_name in wb.sheetnames:
        sheet = wb.get_sheet_by_name(sheet_name)
        if sheet.sheet_state == 'hidden':
            continue
        autosize_ws_columns(sheet)
        # bold column headers
        for cell in sheet["2:2"]:
            cell.font = Font(bold=True)


def autosize_ws_columns(worksheet):
    for col in worksheet.columns:
        column = get_column_letter(col[0].column)
        max_length = max(len(str(cell.value)) for cell in col[1:] if cell.value)
        adjusted_width = (max_length + 2) * 1.1
        worksheet.column_dimensions[column].width = adjusted_width


class Query(object):
    business = Field(BusinessType, business_id=ID(), name=String())
    account_templates = String()
    course_templates = String()


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


    # @login_required
    # @permissions_checker([IsOwner])
    def resolve_account_templates(self, info, **kwargs):
        wb = create_accounts_template()
        return workbook_to_base64(wb)


    # @login_required
    # @permissions_checker([IsOwner])
    def resolve_course_templates(self, info, **kwargs):
        wb = create_course_templates()
        return workbook_to_base64(wb)
