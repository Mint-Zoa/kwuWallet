    from mongoengine import *

connect('kwu')


class User(Document):
    email = StringField(
        required=True,
        unique=True
    )
    password = StringField(
        required=True
    )

    kyc = BooleanField(
        default=False
    )
    wallet = StringField(
        default=""
    )
    type = StringField(
        default="user"
    )
    phone = StringField(
        required=True,
        unique=True
    )
    airdrop = StringField(
        default=""
    )

    meta = {'auto_create_index': True}


class SMS(Document):
    code = IntField(
        required=True
    )

    meta = {'auto_create_index': True}
