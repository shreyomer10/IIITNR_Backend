
# backend.py
from flask import Flask
from flask_cors import CORS
from app.models.mongo import init_mongo
from app.models.firebase import init_firebase
from app.routes.admin import admin_bp
from app.routes.students import student_bp
from app.routes.attendance import attendance_bp
from app.routes.subjects import subjects_bp
from app.routes.login import login_bp
# (Optional) If you need any utility blueprint, you can register it as well.
# from app.routes.utils import utils_bp

app = Flask(__name__)
CORS(app)

# Initialize MongoDB & Firebase
init_mongo(app)
init_firebase()

# Register Blueprints (the URL prefixes here define the external endpoints)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(subjects_bp, url_prefix='/subject')
app.register_blueprint(login_bp, url_prefix='/login')
# If you registered a utils blueprint, add it as needed

@app.route('/')
def home():
    return "Welcome to the IIITNR App Backend!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

