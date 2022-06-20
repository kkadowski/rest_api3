from os import access
from flask import Blueprint, request, jsonify, app
from werkzeug.security import check_password_hash, generate_password_hash
import src.constants.http_status_codes as status_codes
import validators
from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if len(password) < 8:
        return jsonify({"error":"Password to short!"}), status_codes.HTTP_400_BAD_REQUEST
    if len(username) < 3:
        return jsonify({"error":"Username to short!"}), status_codes.HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({"error":"Username should be alphanumeric!"}), status_codes.HTTP_400_BAD_REQUEST
     
    if not validators.email(email):     
        return jsonify({"error":"Email is not valid!"}), status_codes.HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error":"Email is taken!"}), status_codes.HTTP_409_CONFLICT
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error":"Username is taken!"}), status_codes.HTTP_409_CONFLICT
    
    pwd_hash = generate_password_hash(password)
    
    user = User(username = username, password = pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message":"User created",
        "user":{
            'username': username, 'email': email
        }
    }), status_codes.HTTP_201_CREATED


@auth.get("/me")
def me():
    return {"user": "me"}