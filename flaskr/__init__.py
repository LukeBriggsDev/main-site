import os

from flask import Flask


def create_app(test_config=None):
    # create and configure app (factory function)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='YH-T?F/_)q&jw{ljW$l',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import about
    app.register_blueprint(about.bp)

    from . import projects
    app.register_blueprint(projects.bp)

    from . import index
    app.register_blueprint(index.bp)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    # default route to index
    app.add_url_rule('/', endpoint='index')

    return app
