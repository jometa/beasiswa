import os
from flask import Flask, render_template, session, redirect

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
      SECRET_KEY='124sdsd'
    )

    if test_config is None:
        # It probably fail, but it must shut up!!
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        # Ensure instance path exists
        os.makedirs(app.instance_path)
    except OSError:
        # So it already exists... do nothing
        pass

    # Register db session hook, and db seed command
    from . import model
    model.init_app(app)

    # Register auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # Register app blueprint
    from . import main_app
    app.register_blueprint(main_app.bp)
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        if session.get('user_id', None) is not None:
            return redirect('/app/data')
        return render_template('index.html')

    return app