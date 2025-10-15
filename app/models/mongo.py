# app/mongo.py
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_mongo(app):
    app.config["MONGO_URI"] = app.config.get("MONGO_URI")

# Define global collection variables for use in routes
def get_teachers_collection():
    return mongo.db.teachers

def get_students_collection():
    return mongo.db.primary_db

def get_admins_collection():
    return mongo.db.admins

def get_subjects_collection():
    return mongo.db.subjects

def get_attendance_collection():
    return mongo.db.attendance

def get_attendance_string_collection():
    return mongo.db.attendance_string

def get_teachers_copy_collection():
    return mongo.db.teachers_copy

# Mapping for different data types (used in upload endpoint)
# collection_map = {
#     "Subjects": mongo.db.subjectsAdmin,
#     "Teachers": mongo.db.teacherAdmin,
#     "MainDB": mongo.db.primary_db_admin
# }
def get_collection_map():
    return {
        "Subjects": mongo.db.subjectsAdmin,
        "Teachers": mongo.db.teacherAdmin,
        "MainDB": mongo.db.primary_db_admin
    }