from flask import jsonify


def error_response(message, code, http_status):
    response = jsonify({"error": message, "code": code})
    response.status_code = http_status
    return response


def success_response(data, http_status=200):
    response = jsonify(data)
    response.status_code = http_status
    return response
