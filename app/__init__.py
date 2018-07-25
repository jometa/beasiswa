import os
from flask import Flask

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
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app