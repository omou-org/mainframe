from openpyxl import load_workbook

def process_accounts(sheet):
    pass

def process_categories(sheet):
    pass

def process_courses(sheet):
    pass

def process_import(path, file_type):
    wb = load_workbook(filename=path)
    sheet = wb.active
    last_col = sheet.max_column
    sheets = wb.sheetnames
    print('sheet name' , sheets)
    sheet_ranges = sheet['A3'].value
    return (path, file_type)

column_names = {
    "students": [
        'first name',
        'last name',
        'email',
        'date of birth',
        'school',
        'grade',
        'parent first name',
        'parent email'
    ],
    "parent" : [
        "first name",
        "last name",
        "email",
        "phone",
        "zip code"
    ],
    "instructors" : [
        "first name",
        "last name",
        "email",
        "phone",
        "date of birth",
        "teaching subjects",
        "biography",
        "years of experience"
    ]
}