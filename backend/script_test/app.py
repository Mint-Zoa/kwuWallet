import datetime
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_jwt_extended import (jwt_required, create_access_token)
from werkzeug.debug import DebuggedApplication
from models import auth, error, wallet, admin

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'KW-platform'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=90)
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
CORS(app)

def isValidInput(datas):
    for chk in datas:
        if request.form.get(chk) == "" or request.form.get(chk) == None:
            return False
    return True

@jwt.unauthorized_loader
def unauthorized_response(callback):
    response = {
        "success": False,
        "message": "not logged in\nunauthorized response"
    }

    return jsonify(response), 403


@jwt.invalid_token_loader
def invalid_token_loader(callback):
    response = {
        "success": False,
        "message": "not logged in\ninvalid token loaded"
    }

    return jsonify(response), 403


@app.route('/')
def hello():
    return jsonify({
        "status": True,
        "msg": "Server is running now."
    }), 200


@app.route('/auth/login', methods=['POST'])
def auth_login():
    if isValidInput(['email', 'password']):
        return auth.Auth().login()
    else:
        return error.Error().invalid_input()


@app.route('/auth/register', methods=['POST'])
def auth_register():
    if isValidInput(['email', 'password', 'phone']):
        return auth.Auth().register()
    else:
        return error.Error().invalid_input()


@app.route('/auth/sms/get', methods=['POST'])
@jwt_required
def auth_sms_get():
    if isValidInput(['tel']):
        return auth.SMS().get(get_jwt_identity()['email'])
    else:
        return error.Error().invalid_input()


@app.route('/wallet/new', methods=['POST'])
@jwt_required
def wallet_new():
    return wallet.Wallet().new(get_jwt_identity()["email"])


@app.route('/wallet/balance', methods=['POST'])
@jwt_required
def wallet_balance():
    return wallet.Wallet().balance(get_jwt_identity()["email"])


@app.route('/wallet/atcg_old/transfer', methods=['POST'])
@jwt_required
def wallet_atcg_old_transfer():
    """
    if isValidInput(['to', 'amount']):
        return wallet.ATCG().transfer(get_jwt_identity()["email"])
    else:
        return error.Error().invalid_input()
    """

    return error.Error().deprecated_library()


@app.route('/wallet/atcg/transfer', methods=['POST'])
@jwt_required
def wallet_atcg_transfer():
    if isValidInput(['to', 'amount', 'ticket', 'code']):
        return admin.Admin().pending_add(get_jwt_identity()["email"])
    else:
        return error.Error().invalid_input()


@app.route('/wallet/eth/transfer', methods=['POST'])
@jwt_required
def wallet_eth_transfer():
    if isValidInput(['to', 'amount']):
        return wallet.ETH().transfer(get_jwt_identity()["email"])
    else:
        return error.Error().invalid_input()


@app.route('/admin/master/login', methods=['POST'])
def admin_master_login():
    if isValidInput(['email', 'password']):
        return admin.Master().login()
    else:
        return error.Error().invalid_input()


@app.route('/admin/master/register', methods=['POST'])
def admin_master_register():
    return admin.Master().register()


@app.route('/admin/user/login', methods=['POST'])
def admin_user_login():
    if isValidInput(['email', 'password']):
        return admin.User().login()
    else:
        return error.Error().invalid_input()


@app.route('/admin/user/register', methods=['POST'])
@jwt_required
def admin_user_register():
    if isValidInput(['email', 'password', 'amount']):
        return admin.User().register(get_jwt_identity()["role"])
    else:
        return error.Error().invalid_input()


@app.route('/admin/transfer/pending/list', methods=['POST'])
@jwt_required
def admin_transfer_pending_list():
    return admin.Admin().pending_list(
        get_jwt_identity()["role"],
        get_jwt_identity()["email"]
    )


@app.route('/admin/transfer/pending/accept', methods=['POST'])
@jwt_required
def admin_transfer_pending_accept():
    if isValidInput(["pk"]):
        return admin.Admin().pending_accept(get_jwt_identity()["role"])
    else:
        return error.Error().invalid_input()


@app.route('/admin/transfer/pending/deny', methods=['POST'])
@jwt_required
def admin_transfer_pending_deny():
    if isValidInput(["pk"]):
        return admin.Admin().pending_deny(get_jwt_identity()["role"])
    else:
        return error.Error().invalid_input()


@app.route('/admin/manage/list', methods=['POST'])
@jwt_required
def admin_manage_list():
    return admin.Manage().list(get_jwt_identity()["role"])


@app.route('/admin/manage/balance/check', methods=['POST'])
@jwt_required
def admin_manage_balance_check():
    if isValidInput(["email"]):
        return admin.Manage().balance(get_jwt_identity()["role"])
    else:
        return error.Error().invalid_input()


if __name__ == '__main__':
    app.run()
