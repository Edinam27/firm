# wsgi.py
from app import create_app
from config import Config
from flask_wtf.csrf import CSRFProtect

app = create_app(Config)

csrf = CSRFProtect(app)
if __name__ == '__main__':
    app.run(debug=True)
