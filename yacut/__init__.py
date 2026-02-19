from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

swaggerui_blueprint = get_swaggerui_blueprint(
    '/swagger',
    '/static/openapi.yml'
)
app.register_blueprint(swaggerui_blueprint)

from . import api_views, error_handlers, views
