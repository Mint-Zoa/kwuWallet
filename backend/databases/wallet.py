from mongoengine import *

connect('kwu')


class Wallet(Document):
    email = StringField(
        required=True
    )
    address = StringField(
        required=True
    )
    private_key = StringField(
        required=True
    )

    meta = {'auto_create_index': True}
