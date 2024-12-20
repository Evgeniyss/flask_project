from flask import jsonify


def handle_404(e):
    """
    Custom handler for 404 errors.

    Parameters:
    - e: The exception object.

    Returns:
    - Flask response for a 404 error.
    """
    response = jsonify({'error': 'Not Found', 'message': str(e)})
    response.status_code = 404
    return response


def handle_400(e):
    """
    Custom handler for 400 errors.

    Parameters:
    - e: The exception object.

    Returns:
    - Flask response for a 400 error.
    """
    response = jsonify({'error': 'Wrong format', 'message': str(e)})
    response.status_code = 400
    return response
