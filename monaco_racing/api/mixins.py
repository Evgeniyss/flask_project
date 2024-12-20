from flask import request
from flask_restful import abort
from playhouse.flask_utils import get_object_or_404
from typing import Type, Dict, Any, Union
from retry import retry
from .utils import output_format


class ApiMixin:
    """
    A mixin providing common functionality for working with APIs and databases.
    """

    @retry(tries=3, delay=1)
    def get_ordered_items(self, model: Type, code: int, field: str) -> Dict[str, Union[str, int, Any]]:
        """
        Get ordered items from the database based on the specified model, code, and field.

        Args:
            model (Type[ModelSelect]): The Peewee model class.
            code (int): The HTTP status code.
            field (str): The field to order the results by.

        Returns:
            Dict[str, Union[List[Dict[str, Any]], str]]: The formatted output.

        Raises:
            HTTPException: If the format is not specified.
        """
        if not hasattr(model, field):
            abort(404, message='This field is not related to {model} model')

        order, repr_format = self.get_request_params()

        if order == 'desc':
            result = model.select().order_by(getattr(model, field).desc()).dicts()
        else:
            result = model.select().order_by(getattr(model, field).asc()).dicts()

        if not result:
            return output_format({}, 404, repr_format)

        return output_format(result, code, repr_format)

    @retry(tries=3, delay=1)
    def get_single_item(self, model: Type, code: int, lookup: Any) -> Dict[str, Union[str, int, Any]]:
        """
        Get a single item from the database based on the specified model, code, and lookup value.

        Args:
            model (Type[ModelSelect]): The Peewee model class.
            code (int): The HTTP status code.
            lookup (Any): The value to lookup in the model.

        Returns:
            Dict[str, Union[Dict[str, Any], str]]: The formatted output.

        Raises:
            HTTPException: If the format is not specified.
        """
        repr_format = self.get_request_params()[1]

        result = get_object_or_404(model, lookup).to_dict()

        if not result:
            return output_format({}, 404, repr_format)

        return output_format(result, code, repr_format)

    def get_request_params(self):
        """
        Get the request parameters, including order and format.

        Returns:
            Tuple[str, str]: A tuple containing order and repr_format.
        """
        order = request.args.get('order', 'asc')
        repr_format = request.args.get('format')

        if repr_format is None:
            abort(400, message='Format must be specified as json or xml')

        return order, repr_format
