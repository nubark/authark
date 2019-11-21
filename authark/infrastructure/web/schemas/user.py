from marshmallow import Schema, fields, EXCLUDE


class UserAuthSchema(Schema):
    tenant = fields.Str(required=True, load_only=True, example="knowark")
    username = fields.Str(required=True, example="amlopez")
    email = fields.Email(required=True, example="amlopez@nubark.com")
    password = fields.Str(required=True, load_only=True, example="secret")
    name = fields.Str(example="Andrés Manuel López")
    attributes = fields.Mapping(example="{}")


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(required=True, data_key='id',
                    example="f52706c8-ac08-4f9d-a092-8038d1769825")
    username = fields.Str(example="jarango")
    email = fields.Str(example="jarango@ops.servagro.com.co")
    name = fields.Str(example="Jaime Arango")
    attributes = fields.Mapping()
