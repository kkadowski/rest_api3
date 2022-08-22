import src.constants.http_status_codes as status_codes
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Bookmark, db

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods =['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'POST':
       
        body = request.get_json().get('body','')
        url =  request.get_json().get('url','')
        
        if not validators.url(url):
            return jsonify({
                "error" : "Enter a valid url"
            }), status_codes.HTTP_400_BAD_REQUEST
            
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "error" : "Url already exist in database."
            }), status_codes.HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
          'id': bookmark.id,
          'body': bookmark.body,
          'url': bookmark.url,
          'shot_url': bookmark.short_url,
          'visits': bookmark.visits,
          'created_at': bookmark.created_at,
          'updated_at' : bookmark.updated_at
        }), status_codes.HTTP_201_CREATED
        
    else:
        bookmarks = Bookmark.query.filter_by(user_id = current_user)
        data = []
        for bookmark in bookmarks.items:
            data.append({
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'shot_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at' : bookmark.updated_at   
            }), status_codes.HTTP_201_CREATED
    
    return jsonify({
        'data': data
    }), status_codes.HTTP_200_OK