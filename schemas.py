from marshmallow import Schema, fields, validate, ValidationError

class GameSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1))
    year = fields.Integer(required=True, validate=validate.Range(min=1950, max=2100))
    price = fields.Float(required=True, validate=validate.Range(min=0.0))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=4))
