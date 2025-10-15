# app/routes/utils.py
def get_all_students_for_subject(coursecode, admission_year, branch):
    from app.models.mongo import get_students_collection
    query = {}
    if coursecode:
        query["Course_Code"] = coursecode
    if admission_year:
        query["Admission_Year"] = admission_year
    if branch and branch != "0":
        full_branch = f"B.Tech./{branch}"
        query["Program"] = full_branch
    else:
        query["Course_Status"] = "New"
    students = get_students_collection().find(query)
    admission_nos = [student['Admission_No'] for student in students]
    return admission_nos
