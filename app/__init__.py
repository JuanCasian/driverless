from flask import Flask, render_template
from flask_bootstrap import Bootstrap

def create_app():
    app = Flask(__name__)

    bootstrap = Bootstrap(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0', port=4242)