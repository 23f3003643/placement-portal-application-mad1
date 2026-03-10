from flask import Flask
from extensions import db, login_manager
from models import create_admin
from routes import init_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'placement-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager.init_app(app)

# Register all routes
init_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
