from flask import Flask
from .extensions import db, migrate
from .config import Config
from .routes import api
from .models import Employee, Organization, OrganizationResponsible, Tender, Bid, BidReview


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(api)

    db.init_app(app)
    migrate.init_app(app, db)

    return app

    if __name__ == '__main__':
        app.run(debug=True)
