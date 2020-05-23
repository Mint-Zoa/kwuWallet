from flask import request, jsonify
from databases import auth
from models.error import Error
import app
import boto3
from random import randint


class Auth(object):
    @staticmethod
    def register():
        try:
            email = str(request.form['email'])
            password = str(app.bcrypt.generate_password_hash(request.form['password']))
            phone = request.form['phone'].replace("-", "")
            try:
                airdrop = request.form['airdrop']
            except Exception as e:
                print(e)
                airdrop = ""

            auth.User(
                email=email,
                password=password,
                phone=phone,
                airdrop=airdrop
            ).save()

            return jsonify({
                "success": True,
                "msg": "successful created new user",
                "wallet": "",
                "accessToken": app.create_access_token(identity={
                    "email": email,
                    "wallet": ""
                })
            }), 200
        except Exception as e:
            print(e)
            return Error.id_or_phone_overlapped()

    @staticmethod
    def login():
        email = str(request.form['email'])
        password = str(request.form['password'])
        user_object = auth.User.objects(email=email)

        if len(user_object) == 0:
            return Error.invalid_input()
        else:
            if app.bcrypt.check_password_hash(eval(user_object[0].password), password):
                return jsonify({
                    "success": True,
                    "wallet": user_object[0].wallet,
                    "accessToken": app.create_access_token(identity={
                        "email": user_object[0].email,
                        "wallet": user_object[0].wallet
                    })
                }), 200
            else:
                return Error.wrong_password()


class SMS(object):
    def __init__(self):
        # AWS AMI
        self.client = boto3.client(
            "sns",
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",
            region_name="region_name"
        )

    def get(self, email):
        user_object = auth.User.objects(email=email).first()
        tel = request.form['tel'].replace("-", "")

        if tel == user_object.phone.replace("-", ""):
            code = randint(100000, 999999)

            pk = auth.SMS(code=code).save().pk
            self.client.publish(
                PhoneNumber=tel,
                Message="[KW] Verification code: {}\nDo not share this code anybody by all means."
                    .format(code)
            )

            return jsonify({
                "success": True,
                "msg": "Verification code sent successfully.\nCheck your phone SMS.",
                "ticket": str(pk)
            }), 200
        else:
            return jsonify({
                "success": False,
                "msg": "Not your account phone number."
            }), 200

    @staticmethod
    def validate(ticket, code):
        ticket_object = auth.SMS.objects(pk=ticket).first()
        if ticket_object.code == int(code):
            ticket_object.delete()
            return True
        else:
            return False
