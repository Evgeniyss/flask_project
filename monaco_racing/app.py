from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from .db.initialize_db import initialize_database
from .db.models import db, Report, Driver
from .api.utils import output_xml
from .api.api_views import ReportAPIView, DriverListAPIView, DriverDetailAPIView
from .error_handlers import handle_404, handle_400


def create_app():
    app = Flask(__name__)
    api = Api(app, prefix='/api/v1/')
    swagger = Swagger(app)

    api.representations['application/xml'] = output_xml

    api.add_resource(ReportAPIView, '/report')
    api.add_resource(DriverListAPIView, '/report/drivers/')
    api.add_resource(DriverDetailAPIView, '/report/drivers/<driver_slug>')

    app.register_error_handler(404, handle_404)
    app.register_error_handler(400, handle_400)

    with app.app_context():
        db.connect()
        if not Report.table_exists() and not Driver.table_exists():
            initialize_database()
        db.close()

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
