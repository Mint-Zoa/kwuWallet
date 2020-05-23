from flask import jsonify, request
from databases import admin, auth
from models.error import Error
from models.wallet import ATCG_func, ETH
from models.auth import SMS
import json
from collections import OrderedDict
import app


class Master(object):
    @staticmethod
    def login():
        email = str(request.form['email'])
        password = str(request.form['password'])
        master_object = admin.Master.objects(email=email)

        if len(master_object) == 0:
            return Error.invalid_input()
        else:
            if app.bcrypt.check_password_hash(str(master_object[0].password), password):
                return jsonify({
                    "success": True,
                    "type": "master",
                    "accessToken": app.create_access_token(identity={
                        "role": "master"
                    })
                }), 200
            else:
                return Error.wrong_password()


    @staticmethod
    def register():
        try:
            email = "email"
            password = "password"
            password = app.bcrypt.generate_password_hash(password)

            admin.Master(
                email=email,
                password=password
            ).save()

            return jsonify({
                "success": True,
            }), 200
        except Exception as e:
            print(e)
            return Error.unexpected_error()


class User(object):
    @staticmethod
    def register(role):
        if role == "master":
            try:
                email = str(request.form['email'])
                password = str(app.bcrypt.generate_password_hash(request.form['password']))
                amount = str(request.form['amount'])

                admin.Admin(
                    email=email,
                    password=password,
                    amount=amount
                ).save()

                return jsonify({
                    "success": True,
                    "msg": "successful created new admin user"
                }), 200
            except Exception as e:
                print(e)
                return Error.id_overlapped()
        else:
            return Error.permission_deny()

    @staticmethod
    def login():
        email = str(request.form['email'])
        password = str(request.form['password'])
        user_object = admin.Admin.objects(email=email)

        if len(user_object) == 0:
            return Error.user_not_found()
        else:
            if app.bcrypt.check_password_hash(eval(user_object[0].password), password):
                return jsonify({
                    "success": True,
                    "accessToken": app.create_access_token(identity={
                        "role": "admin",
                        "email": user_object[0].email
                    })
                }), 200
            else:
                return Error.wrong_password()


class Admin(object):
    @staticmethod
    def pending_list(role, email):
        if role == "admin":
            pending_object = admin.Pending.objects(status=False)
            pending_data = OrderedDict()

            pending_data_tmp = list()

            admin_object = admin.Admin.objects(email=email).first()
            for tmp_object in pending_object:
                if int(admin_object.amount) >= int(tmp_object.amount):
                    tmp_data = OrderedDict()
                    tmp_data["pk"] = str(tmp_object.pk)
                    tmp_data["email"] = tmp_object.email
                    tmp_data["to"] = tmp_object.to
                    tmp_data["amount"] = tmp_object.amount
                    pending_data_tmp.append(tmp_data)

            pending_data["data"] = pending_data_tmp
            pending_data["length"] = len(pending_data_tmp)

            return jsonify({
                "success": True,
                "msg": "Get pending list successfully.",
                "data": json.dumps(pending_data, ensure_ascii=False)
            })
        else:
            return Error.permission_deny()

    @staticmethod
    def pending_accept(role):
        if role == "admin":
            try:
                pending_object = admin.Pending.objects(pk=str(request.form["pk"])).first()

                response, response_code = ATCG_func().transfer(
                    email=pending_object.email,
                    to=pending_object.to,
                    amount=pending_object.amount
                )

                pending_object.status = True
                pending_object.save()

                return response, response_code
            except Exception as e:
                print(e)
                return jsonify({
                    "success": False,
                    "msg": "Ticket Rejected"
                }), 200
        else:
            return Error.permission_deny()

    @staticmethod
    def pending_add(email):
        to = request.form["to"]
        amount = request.form["amount"]
        ticket = request.form["ticket"]
        code = request.form["code"]

        if SMS.validate(ticket, code):
            atcg_balance = ATCG_func().balance(email)

            if atcg_balance * 0.3 >= float(amount):
                admin.Pending(
                    email=email,
                    to=to,
                    amount=amount
                ).save()

                return jsonify({
                    "success": True,
                    "msg": "add atcg pending list"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "msg": "Not enough ATCG!!"
                }), 200
        else:
            return jsonify({
                "success": False,
                "msg": "SMS Verification Failed."
            }), 200

    @staticmethod
    def pending_deny(role):
        if role == "admin":
            try:
                admin.Pending.objects(pk=str(request.form["pk"])).first().delete()

                return jsonify({
                    "success": True,
                    "msg": "Ticket deny successfully."
                }), 200
            except Exception as e:
                print(e)
                return jsonify({
                    "success": False,
                    "msg": "Ticket Rejected"
                })
        else:
            return Error.permission_deny()


class Manage(object):
    @staticmethod
    def list(role):
        if role == "admin":
            user_objects = auth.User.objects()
            user_list = OrderedDict()
            user_list_tmp = list()
            for user_object in user_objects:
                tmp_data = OrderedDict()
                tmp_data["email"] = user_object.email
                tmp_data["phone"] = user_object.phone
                tmp_data["wallet"] = user_object.wallet
                tmp_data["airdrop"] = user_object.airdrop
                user_list_tmp.append(tmp_data)

            user_list["data"] = user_list_tmp
            user_list["length"] = len(user_list_tmp)

            return jsonify({
                "success": True,
                "msg": "Get pending list successfully.",
                "data": json.dumps(user_list, ensure_ascii=False)
            }), 200
        else:
            return Error.permission_deny()

    @staticmethod
    def balance(role):
        if role == "admin":
            email = request.form['email']
            atcg_balance = ATCG_func().balance(email=email)
            eth_balance = ETH().balance(email=email)

            return jsonify({
                "success": True,
                "msg": "Get user balance successfully.",
                "atcg": atcg_balance,
                "eth": eth_balance
            }), 200
        else:
            return Error.permission_deny()
