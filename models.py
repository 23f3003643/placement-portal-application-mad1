from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from datetime import datetime


# =================================================
# USER MODEL
# =================================================

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # admin / student / company

    approved = db.Column(db.Boolean, default=False)

    active = db.Column(db.Boolean, default=True)


    # ---------- STUDENT FIELDS ----------

    student_id = db.Column(db.String(50))

    phone = db.Column(db.String(20))

    degree = db.Column(db.String(100))

    branch = db.Column(db.String(100))

    cgpa = db.Column(db.String(10))

    year = db.Column(db.String(10))

    resume = db.Column(db.String(200))  # resume file path


    # ---------- COMPANY FIELDS ----------

    hr_name = db.Column(db.String(100))

    hr_contact = db.Column(db.String(20))

    website = db.Column(db.String(200))

    description = db.Column(db.Text)


    def __repr__(self):
        return f"<User {self.email}>"



# =================================================
# PLACEMENT DRIVE MODEL
# =================================================

class PlacementDrive(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    job_title = db.Column(db.String(150), nullable=False)

    job_description = db.Column(db.Text, nullable=False)

    eligibility = db.Column(db.String(200), nullable=False)

    min_cgpa = db.Column(db.String(10))

    salary = db.Column(db.String(50))

    location = db.Column(db.String(100))

    deadline = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(20), default='Pending')
    # Pending / Approved / Closed

    applications = db.relationship('Application', backref='drive', lazy=True)

    # relationship to company
    company = db.relationship(
        'User',
        backref=db.backref('drives', lazy=True)
    )

    def __repr__(self):
        return f"<Drive {self.job_title}>"


# =================================================
# APPLICATION MODEL
# =================================================

class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey('placement_drive.id'),
        nullable=False
    )

    status = db.Column(db.String(20), default='Applied')

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', foreign_keys=[student_id])

    def __repr__(self):
        return f"<Application {self.id}>"


# =================================================
# CREATE DEFAULT ADMIN
# =================================================

def create_admin():

    admin = User.query.filter_by(role='admin').first()

    if not admin:

        admin = User(
            name='Admin',
            email='admin@123.com',
            password=generate_password_hash('123admin'),
            role='admin',
            approved=True
        )

        db.session.add(admin)

        db.session.commit()