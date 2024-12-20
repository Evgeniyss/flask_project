import pytest
from bs4 import BeautifulSoup
from monaco_racing.app import create_app
from monaco_racing.api.utils import get_report_build, output_xml
from src.report.constants import (ABBREVIATIONS_FILE_PATH as file_path,
                                  START_LOG_FILE_PATH as start_log_path,
                                  END_LOG_FILE_PATH as end_log_path)
from flask import Flask
from flask.testing import FlaskClient
from monaco_racing.error_handlers import handle_400


@pytest.fixture
def app() -> Flask:
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize('url, expected_result', [
    ('/api/v1/report?format=json', 200),
    ('/api/v1/report?format=json', 200),
    ('/api/v1/report?format=xml', 200),
    ('/api/v1//invalid_url', 404),
    ('/api/v1/report', 400)
])
def test_report(client, url, expected_result):
    response = client.get(url)
    assert response.status_code == expected_result


@pytest.mark.parametrize('url, expected_result', [
    ('/api/v1/report/drivers/?format=json', 200),
    ('/api/v1/report/drivers/?format=json', 200),
    ('/api/v1//invalid_url', 404),
    ('/api/v1/report/drivers/', 400),
])
def test_driver_list(client, url, expected_result):
    response = client.get(url)
    assert response.status_code == expected_result


@pytest.mark.parametrize('url, expected_result', [
    ('/api/v1/report/drivers/SVF?format=json', 200),
    ('/api/v1/report/drivers/DRR?format=xml', 200),
    ('/api/v1//invalid_url', 404),
    ('/api/v1/report/drivers/invalid_id', 400),
    ('/api/v1/report/drivers/SVF', 400)
])
def test_driver_detail(client, url, expected_result):
    response = client.get(url)
    assert response.status_code == expected_result


def test_report_template(client):
    response = client.get('/report')
    soup = BeautifulSoup(response.data, 'lxml')


def test_driver_detail_template(client):
    response = client.get('/report/drivers/SVF')
    soup = BeautifulSoup(response.data, 'lxml')


def test_driver_list_template(client):
    response = client.get('/report/drivers/')
    soup = BeautifulSoup(response.data, 'lxml')


def test_get_report_build_invalid_start_log():
    with pytest.raises(TypeError):
        get_report_build(path=str(file_path),
                         order='asc',
                         driver='',
                         start_log=123,
                         end_log=str(end_log_path))


def test_get_report_build_invalid_end_log():
    with pytest.raises(TypeError):
        get_report_build(path=str(file_path),
                         order='asc',
                         driver='',
                         start_log=str(start_log_path),
                         end_log=123)


def test_get_report_build_invalid_order():
    with pytest.raises(TypeError):
        get_report_build(path=str(file_path),
                         order='invalid',
                         driver='',
                         start_log=str(start_log_path),
                         end_log=str(end_log_path))


def test_get_report_build_invalid_file_path():
    with pytest.raises(TypeError):
        get_report_build(path=123,
                         order='asc',
                         driver='',
                         start_log=str(start_log_path),
                         end_log=str(end_log_path))


class TestApiMixin:
    @pytest.mark.parametrize("endpoint, expected_status", [
        ('api/v1/report?format=json', 200),
        ('api/v1/report/drivers/SVF?format=json', 200),
        ('api/v1/report?format=xml', 200),
        ('api/v1/report', 400),
    ])
    def test_get_endpoints(self, app: Flask, client: FlaskClient, endpoint, expected_status):
        response = client.get(endpoint)
        assert response.status_code == expected_status

    def test_get_ordered_items(self, app: Flask, client: FlaskClient):
        response = client.get('api/v1/report?format=json&order=desc')
        assert response.status_code == 200

    def test_get_single_item(self, app: Flask, client: FlaskClient):
        driver_slug = 'SVF'
        response = client.get(
            f'api/v1/report/drivers/{driver_slug}?format=json')
        assert response.status_code == 200

    def test_get_request_params(self, app: Flask, client: FlaskClient):
        response = client.get('api/v1/report?format=json&order=asc')
        assert response.status_code == 200

    def test_get_request_params_no_format(self, app: Flask, client: FlaskClient):
        response = client.get('api/v1/report')
        assert response.status_code == 400
        assert 'Format must be specified as json or xml' in response.json['message']


class TestReportAPIView:
    def test_get(self, app, client):
        response = client.get('api/v1/report?format=json')
        assert response.status_code == 200


class TestDriverListAPIView:
    def test_get(self, app, client):
        response = client.get('api/v1/report/drivers/?format=json')
        assert response.status_code == 200


class TestDriverDetailAPIView:
    def test_get(self, app, client):
        driver_slug = 'SVF'
        response = client.get(
            f'api/v1/report/drivers/{driver_slug}?format=json')
        assert response.status_code == 200


class TestOutputXML:
    def test_output_xml(self, app, client):
        with app.app_context():
            data = {'key': 'value'}
            code = 200
            headers = {'Content-Type': 'application/xml'}
            response = output_xml(data, code, headers)
            assert response.status_code == code
            assert response.headers['Content-Type'] == headers['Content-Type']


class TestHandle400:
    def test_handle_400(self, app, client):
        with app.app_context():
            error_message = 'Error message'
            response = handle_400(error_message)
            assert response.status_code == 400
