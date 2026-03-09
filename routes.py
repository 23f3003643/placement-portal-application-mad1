from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager
from models import User, PlacementDrive, Application

import os
from werkzeug.utils import secure_filename



# USER LOADER

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# INIT ROUTES


def init_routes(app):

    
    # INDEX
    

    @app.route('/')
    def index():
        return render_template('index.html')


   
    # LOGIN
    

    @app.route('/login', methods=['GET', 'POST'])
    def login():

        if request.method == 'POST':

            email = request.form['email']
            password = request.form['password']
            role = request.form['role']

            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):

                if user.role != role:
                    flash("Invalid role selected")
                    return redirect(url_for('login'))

                if not user.active:
                    flash("Account deactivated")
                    return redirect(url_for('login'))

                if user.role == "company" and not user.approved:
                    flash("Company not approved yet")
                    return redirect(url_for('login'))

                login_user(user)

                if user.role == "admin":
                    return redirect(url_for('admin_dashboard'))
                elif user.role == "student":
                    return redirect(url_for('student_dashboard'))
                else:
                    return redirect(url_for('company_dashboard'))

            flash("Invalid credentials")

        return render_template('login.html')


    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))


    # REGISTRATION

    @app.route('/register/student', methods=['GET', 'POST'])
    def register_student():

        if request.method == 'POST':

            user = User(
                name=request.form['name'],
                email=request.form['email'],
                password=generate_password_hash(request.form['password']),
                role='student',
                approved=True,
                student_id=request.form['student_id'],
                phone=request.form['phone'],
                degree=request.form['degree'],
                branch=request.form['branch'],
                cgpa=request.form['cgpa'],
                year=request.form['year']
            )

            db.session.add(user)
            db.session.commit()

            flash("Student registered successfully")
            return redirect(url_for('login'))

        return render_template('register_student.html')


    @app.route('/register/company', methods=['GET', 'POST'])
    def register_company():

        if request.method == 'POST':

            user = User(
                name=request.form['name'],
                email=request.form['email'],
                password=generate_password_hash(request.form['password']),
                role='company',
                approved=False,
                hr_name=request.form['hr_name'],
                hr_contact=request.form['hr_contact'],
                website=request.form['website'],
                description=request.form['description']
            )

            db.session.add(user)
            db.session.commit()

            flash("Company registered. Await admin approval.")
            return redirect(url_for('login'))

        return render_template('register_company.html')


    # ADMIN ROUTES

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():

        if current_user.role != 'admin':
            return redirect(url_for('login'))

        return render_template(
            'admin_dashboard.html',
            total_students=User.query.filter_by(role='student').count(),
            total_companies=User.query.filter_by(role='company').count(),
            total_drives=PlacementDrive.query.count(),
            total_applications=Application.query.count(),
            pending_companies = User.query.filter_by(role='company', approved=False).count(),
            pending_drives = PlacementDrive.query.filter_by(status='Pending').count(),
            applied=Application.query.filter_by(status='Applied').count(),
            shortlisted=Application.query.filter_by(status='Shortlisted').count(),
            selected=Application.query.filter_by(status='Selected').count(),
            rejected=Application.query.filter_by(status='Rejected').count(),
            recent_apps = Application.query.order_by(Application.applied_on.desc()).limit(5).all()
        )

    # ADMIN COMPANIES 

    @app.route('/admin/companies')
    @login_required
    def admin_companies():

        if current_user.role != "admin":
            return redirect(url_for('login'))

        search = request.args.get("search")

        query = User.query.filter_by(role='company')

        if search:
            query = query.filter(
                User.name.ilike(f"%{search}%")
            )

        companies = query.all()

        return render_template(
            "admin_companies.html",
            companies=companies,
            search=search
        )

    # ADMIN STUDENTS 

    @app.route('/admin/students')
    @login_required
    def admin_students():

        if current_user.role != "admin":
            return redirect(url_for('login'))

        search = request.args.get('search')

        query = User.query.filter_by(role='student')

        if search:
            query = query.filter(
                (User.name.ilike(f"%{search}%")) |
                (User.student_id.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%")) |
                (User.phone.ilike(f"%{search}%"))
            )

        students = query.all()

        return render_template(
            "admin_students.html",
            students=students,
            search=search
        )


    #ADMIN DRIVES 

    @app.route('/admin/drives')
    @login_required
    def admin_drives():

        if current_user.role != "admin":
            return redirect(url_for('login'))

        drives = PlacementDrive.query.all()

        return render_template(
            "admin_drives.html",
            drives=drives
        )


    #  ADMIN APPLICATIONS 

    @app.route('/admin/applications')
    @login_required
    def admin_applications():

        if current_user.role != "admin":
            return redirect(url_for('login'))

        applications = Application.query.all()

        return render_template(
            "admin_applications.html",
            applications=applications
        )

    # ADMIN APPROVE COMPANY

    @app.route('/admin/company/approve/<int:id>')
    @login_required
    def approve_company(id):

        if current_user.role != 'admin':
            return redirect(url_for('login'))

        company = User.query.get_or_404(id)

        company.approved = True

        db.session.commit()

        flash("Company approved successfully")

        return redirect(url_for('admin_companies'))

    #aADMIN REJECT COMPANY

    @app.route('/admin/company/reject/<int:id>')
    @login_required
    def reject_company(id):

        if current_user.role != 'admin':
            return redirect(url_for('login'))

        company = User.query.get_or_404(id)
 
        company.approved = False
        company.active = False

        db.session.commit()

        flash("Company rejected")

        return redirect(url_for('admin_companies'))

    #ADMIN APPROVE DRIVE

    @app.route('/admin/approve_drive/<int:id>')
    @login_required
    def approve_drive(id):

        drive = PlacementDrive.query.get_or_404(id)
        drive.status = "Approved"

        db.session.commit()

        flash("Drive approved")
        return redirect(url_for('admin_drives'))

    #ADMIN REJCT DRIVE

    @app.route('/admin/reject_drive/<int:id>')
    @login_required
    def reject_drive(id):

        drive = PlacementDrive.query.get_or_404(id)

        db.session.delete(drive)
        db.session.commit()
 
        flash("Drive rejected")
 
        return redirect(url_for('admin_drives'))

    #BLACKLIST STUDENT

    @app.route('/admin/blacklist_student/<int:id>')
    @login_required
    def blacklist_student(id):

        student = User.query.get_or_404(id)

        student.active = False
        db.session.commit()

        flash("Student blacklisted")
        return redirect(url_for('admin_students'))

    #BLACKLIST COMPANY

    @app.route('/admin/blacklist_company/<int:id>')
    @login_required
    def blacklist_company(id):

        company = User.query.get_or_404(id)

        if company.role != "company":
            flash("Invalid company")
            return redirect(url_for('admin_companies'))

        company.active = False
        db.session.commit()

        flash("Company blacklisted successfully")

        return redirect(url_for('admin_companies'))

    #ACTIVATE COMPANY

    @app.route('/admin/activate_company/<int:id>')
    @login_required
    def activate_company(id):

        company = User.query.get_or_404(id)

        company.active = True
        db.session.commit()

        flash("Company activated")

        return redirect(url_for('admin_companies'))


    #BLACKLIST DRIVE

    @app.route('/admin/blacklist_drive/<int:id>')
    @login_required
    def blacklist_drive(id):

        drive = PlacementDrive.query.get_or_404(id)

        drive.status = "Closed"

        db.session.commit()

        flash("Drive blacklisted")
 
        return redirect(url_for('admin_drives'))


    # COMPANY ROUTES

    # COMPANY DASHBOARD

    @app.route('/company/dashboard')
    @login_required
    def company_dashboard():

        if current_user.role != 'company':
            return redirect(url_for('login'))

        drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()

        total_applications = Application.query.join(PlacementDrive).filter(
            PlacementDrive.company_id == current_user.id
        ).count()

        return render_template(
            'company_dashboard.html',
            active_drives=len([d for d in drives if d.status=='Approved']),
            pending_drives=len([d for d in drives if d.status=='Pending']),
            total_drives=len(drives),
            total_applications=total_applications
        )

    # COMPANY PROFILE
    @app.route('/company/profile', methods=['GET','POST'])
    @login_required
    def company_profile():

        if current_user.role != 'company':
            return redirect(url_for('login'))

        if request.method == 'POST':

            current_user.name = request.form['name']
            current_user.hr_name = request.form['hr_name']
            current_user.hr_contact = request.form['hr_contact']
            current_user.website = request.form['website']
            current_user.description = request.form['description']

            db.session.commit()

            flash("Profile updated successfully")

        return render_template(
            "company_profile.html",
            company=current_user
        )

    
    #CREATE DRIVE

    @app.route('/company/create_drive', methods=['GET','POST'])
    @login_required
    def create_drive():

        if current_user.role != 'company':
            return redirect(url_for('login'))

        if request.method == 'POST':

            drive = PlacementDrive(
                company_id=current_user.id,
                job_title=request.form['job_title'],
                job_description=request.form['job_description'],
                eligibility=request.form['eligibility'],
                min_cgpa=request.form['min_cgpa'],
                salary=request.form['salary'],
                location=request.form['location'],
                deadline=request.form['deadline']
            )

            db.session.add(drive)
            db.session.commit()

            flash("Drive created succesfully")

            return redirect(url_for('company_drives'))

        return render_template('create_drive.html')

    #COMPANY DRIVES

    @app.route('/company/drives')
    @login_required
    def company_drives():

        drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()

        return render_template('company_drive.html', drives=drives)

    #CLOSE DRIVES

    @app.route('/company/close_drive/<int:id>')
    @login_required
    def close_drive(id):

        drive = PlacementDrive.query.get_or_404(id)

        if drive.company_id != current_user.id:
            return redirect(url_for('company_drives'))

        drive.status = "Closed"

        db.session.commit()

        flash("Drive closed")

        return redirect(url_for('company_drives'))

    #DELETE DRIVE

    @app.route('/company/delete_drive/<int:id>')
    @login_required
    def delete_drive(id):

        drive = PlacementDrive.query.get_or_404(id)

        if drive.company_id != current_user.id:
            return redirect(url_for('company_drives'))

        db.session.delete(drive)
        db.session.commit()

        flash("Drive deleted")

        return redirect(url_for('company_drives'))

    #EDIT DRIVE
    @app.route('/company/edit_drive/<int:id>', methods=['GET','POST'])
    @login_required
    def edit_drive(id):

        if current_user.role != 'company':
            return redirect(url_for('login'))

        drive = PlacementDrive.query.get_or_404(id)

        if drive.company_id != current_user.id:
            return redirect(url_for('company_drives'))

        if request.method == 'POST':

            drive.job_title = request.form['job_title']
            drive.job_description = request.form['job_description']
            drive.eligibility = request.form['eligibility']
            drive.min_cgpa = request.form['min_cgpa']
            drive.salary = request.form['salary']
            drive.location = request.form['location']
            drive.deadline = request.form['deadline']

            db.session.commit()

            flash("Drive updated successfully")

            return redirect(url_for('company_drives'))

        return render_template(
            'edit_drive.html',
            drive=drive
        )

    #VIEW APPLICATIONS

    @app.route('/company/drive/<int:drive_id>')
    @login_required
    def drive_applications(drive_id):

        drive = PlacementDrive.query.get_or_404(drive_id)

        applications = Application.query.filter_by(drive_id=drive_id).all()

        return render_template(
            'drive_applications.html',
            drive=drive,
            applications=applications
        )

    @app.route('/company/update_status/<int:app_id>/<string:new_status>')
    @login_required
    def update_status(app_id, new_status):

        if current_user.role != 'company':
            return redirect(url_for('login'))

        application = Application.query.get_or_404(app_id)
        application.status = new_status
        db.session.commit()

        flash("Application status updated")
        return redirect(url_for('company_dashboard'))

    # STUDENT ROUTES

    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():

        if current_user.role != 'student':
            return redirect(url_for('login'))

        my_apps = Application.query.filter_by(student_id=current_user.id).all()

        available_drives = PlacementDrive.query.filter_by(status='Approved').count()

        shortlisted = Application.query.filter_by(
            student_id=current_user.id,
            status='Shortlisted'
        ).count()

        selected = Application.query.filter_by(
            student_id=current_user.id,
            status='Selected'
        ).count()

        return render_template(
            'student_dashboard.html',
            available_drives=available_drives,
            my_applications=len(my_apps),
            shortlisted=shortlisted,
            selected=selected,
            recent_apps=my_apps[:5]
        )

    @app.route('/student/drives')
    @login_required
    def student_drives():

        if current_user.role != 'student':
            return redirect(url_for('login'))

        search = request.args.get('search')
        cgpa = request.args.get('cgpa')

        query = PlacementDrive.query.filter_by(status='Approved')

        if search:
            query = query.filter(
                PlacementDrive.job_title.ilike(f"%{search}%") |
                PlacementDrive.location.ilike(f"%{search}%") |
                PlacementDrive.eligibility.ilike(f"%{search}%")
            )

        if cgpa:
            query = query.filter(
                PlacementDrive.min_cgpa >= cgpa
            )

        drives = query.all()

        applied_ids = [
            app.drive_id for app in Application.query.filter_by(
                student_id=current_user.id
            ).all()
        ]

        return render_template(
            'student_drives.html',
            drives=drives,
            applied_drive_ids=applied_ids,
            search=search,
            cgpa=cgpa
        )

    @app.route('/student/apply/<int:drive_id>')
    @login_required
    def apply_drive(drive_id):

        if current_user.role != 'student':
            return redirect(url_for('login'))

        existing = Application.query.filter_by(
            student_id=current_user.id,
            drive_id=drive_id
        ).first()

        if existing:
            flash("You already applied for this drive")
        else:
            new_app = Application(
                student_id=current_user.id,
                drive_id=drive_id,
                status='Applied'
            )

            db.session.add(new_app)
            db.session.commit()

            flash("Application submitted successfully!")

        return redirect(url_for('student_drives'))

    @app.route('/student/applications')
    @login_required
    def student_applications():

        if current_user.role != 'student':
            return redirect(url_for('login'))

        applications = Application.query.filter_by(
            student_id=current_user.id
        ).all()

        return render_template(
            'student_applications.html',
            applications=applications,
            total=len(applications),
            pending=Application.query.filter_by(
                student_id=current_user.id,
                status='Applied'
            ).count(),
            shortlisted=Application.query.filter_by(
                student_id=current_user.id,
                status='Shortlisted'
            ).count(),
            selected=Application.query.filter_by(
                student_id=current_user.id,
                status='Selected'
            ).count()
        )

    @app.route('/student/profile', methods=['GET', 'POST'])
    @login_required
    def student_profile():

        if current_user.role != 'student':
            return redirect(url_for('login'))
 
        if request.method == 'POST':

            current_user.branch = request.form['branch']
            current_user.cgpa = request.form['cgpa']
            current_user.phone = request.form['phone']

            db.session.commit()

        return render_template(
            'student_profile.html',
            student=current_user
        )

    # RESUME UPLOADING

    UPLOAD_FOLDER = "static/resumes"


    @app.route('/student/upload_resume', methods=['POST'])
    @login_required
    def upload_resume():

        if current_user.role != 'student':
            return redirect(url_for('login'))

        file = request.files['resume']

        if file:

            filename = secure_filename(file.filename)

            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)

            current_user.resume = filename

            db.session.commit()

        return redirect(url_for('student_profile'))