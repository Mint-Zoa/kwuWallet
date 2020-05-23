from mongoengine import *

connect('kwu')


class Master(Document):
    email = StringField(
        required=True
    )
    password = StringField(
        required=True
    )

    meta = {'auto_create_index': True}


class Admin(Document):
    email = StringField(
        required=True,
        unique=True
    )
    password = StringField(
        required=True
    )

    amount = StringField(
        required=True
    )

    meta = {'auto_create_index': True}


class Pending(Document):
    email = StringField(
        required=True
    )

    to = StringField(
        required=True
    )
    amount = StringField(
        required=True
    )

    status = BooleanField(
        default=False
    )

    meta = {'auto_create_index': True}
