from flask import Flask, request, jsonify
from file_sharing_api import FileShareAPI

app = Flask(__name__)
api = FileShareAPI()


def _bad_request(msg: str):
    return jsonify({'status_code': 400, 'message': msg}), 400


@app.route("/", methods=["GET"])
def index():
    return jsonify({'message': 'FileShareAPI Flask wrapper', 'status': 'ok'})


@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json(silent=True) or {}
    email = body.get('email')
    organization_id = body.get('organization_id')
    name = body.get('name')

    if not email or not organization_id or not name:
        return _bad_request('Missing required fields: email, organization_id, name')

    resp = api.create_user(email, organization_id, name)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = api.get_user(user_id)
    if not user:
        return jsonify({'status_code': 404, 'message': 'User not found'}), 404

    data = {
        'user_id': user.user_id,
        'email': user.email,
        'organization_id': user.organization_id,
        'name': user.name,
        'created_at': user.created_at.isoformat()
    }
    return jsonify({'status_code': 200, 'message': 'User retrieved', 'data': data}), 200


@app.route('/files', methods=['POST'])
def create_file():
    body = request.get_json(silent=True) or {}
    owner_id = body.get('owner_id')
    name = body.get('name')
    visibility = body.get('visibility')
    content = body.get('content', '')

    if not owner_id or not name or not visibility:
        return _bad_request('Missing required fields: owner_id, name, visibility')

    resp = api.create_file(owner_id, name, visibility, content)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/files/<file_id>', methods=['GET'])
def get_file(file_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return _bad_request('Missing query param: user_id')

    resp = api.get_file(file_id, user_id)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/files/<file_id>', methods=['PUT'])
def update_file(file_id):
    body = request.get_json(silent=True) or {}
    user_id = body.get('user_id')
    content = body.get('content')

    if not user_id or content is None:
        return _bad_request('Missing required fields: user_id, content')

    resp = api.update_file(file_id, user_id, content)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return _bad_request('Missing query param: user_id')

    resp = api.delete_file(file_id, user_id)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/files/<file_id>/share', methods=['POST'])
def share_file(file_id):
    body = request.get_json(silent=True) or {}
    user_id = body.get('user_id')
    target_user_id = body.get('target_user_id')
    permission_type = body.get('permission_type', 'read')

    if not user_id or not target_user_id:
        return _bad_request('Missing required fields: user_id, target_user_id')

    resp = api.share_file(file_id, user_id, target_user_id, permission_type)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/files/<file_id>/permissions', methods=['GET'])
def file_permissions(file_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return _bad_request('Missing query param: user_id')

    resp = api.get_file_permissions(file_id, user_id)
    return jsonify(resp.to_dict()), resp.status_code


@app.route('/authorize', methods=['POST'])
def authorize_check():
    """Non-destructive authorization check endpoint.

    JSON: { file_id, user_id, action }
    Returns: { allowed: True|False }
    """
    body = request.get_json(silent=True) or {}
    file_id = body.get('file_id')
    user_id = body.get('user_id')
    action = body.get('action')

    if not file_id or not user_id or not action:
        return _bad_request('Missing required fields: file_id, user_id, action')

    allowed = api._check_authorization(file_id, user_id, action)
    return jsonify({'allowed': bool(allowed)}), 200


@app.route('/files', methods=['GET'])
def list_files():
    # Simple debug listing of all files
    files = api.get_all_files()
    data = [
        {
            'file_id': f.file_id,
            'name': f.name,
            'owner_id': f.owner_id,
            'visibility': f.visibility,
            'created_at': f.created_at.isoformat()
        }
        for f in files
    ]
    return jsonify({'status_code': 200, 'message': 'Files listed', 'data': {'files': data}}), 200


@app.route('/reset', methods=['POST'])
def reset_api():
    api.reset()
    return jsonify({'status_code': 200, 'message': 'API state reset'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
