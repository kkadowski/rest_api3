import re
from xml.etree.ElementTree import indent
from flask import Blueprint, request, jsonify
from  werkzeug.security import check_password_hash, generate_password_hash
from  src.constants.http_status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token

auth = Blueprint("auth", __name__, url_prefix= "/api/v1/auth")


@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
    if len(password) < 8:
        return jsonify({"Error": " Password to short"}), HTTP_400_BAD_REQUEST
     
    if len(username) < 4:
        return jsonify({"Error": " Username to short"}), HTTP_400_BAD_REQUEST
       
    if not username.isalnum() or " " in username:
        return jsonify({"Error": " Username should be alphanumeric"}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"error": "Email is not valid"}), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email is taken"}), HTTP_409_CONFLICT
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username is taken"}), HTTP_409_CONFLICT
    
    pwd_hash = generate_password_hash(password)
    user = User(username=username, password=pwd_hash, email=email)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User created",
                    'user': {"username":username, "email":email}
                    }), HTTP_201_CREATED
    
@auth.post('/login')
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')
    
    user=User.query.filter_by(email=email).first()
    if user:
        is_pass_correct = check_password_hash(user.password, password)
        
        if is_pass_correct:
            refresh = create_refresh_token(identity = user.id)
            access = create_refresh_token(identity = user.id)

            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
   
@auth.get("/me")
def me():
    return jsonify({"user":"me"})