from flask import jsonify


def success_response(data=None, message=None, status_code=200, meta=None):
    body = {"success": True}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    if meta is not None:
        body["meta"] = meta
    return jsonify(body), status_code


def error_response(error, status_code=400):
    return jsonify({"success": False, "error": error}), status_code
