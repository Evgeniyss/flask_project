from flask_restful import Resource
from flasgger import swag_from
from ..db.models import Driver, Report
from .mixins import ApiMixin


class ReportAPIView(Resource, ApiMixin):
    """
    Report API
    """
    @swag_from('docs/report_doc.yaml')
    def get(self):
        return self.get_ordered_items(model=Report,
                                      code=200,
                                      field='timestamp')


class DriverListAPIView(Resource, ApiMixin):
    """
    Driver List API
    """
    @swag_from('docs/driver_list_doc.yaml')
    def get(self):
        return self.get_ordered_items(model=Driver,
                                      code=200,
                                      field='driver_name')


class DriverDetailAPIView(Resource, ApiMixin):
    """
    Driver Detail API
    """
    @swag_from('docs/driver_detail_doc.yaml')
    def get(self, driver_slug: str):
        return self.get_single_item(model=Driver,
                                    code=200,
                                    lookup=(Driver.code == driver_slug)
                                    )
