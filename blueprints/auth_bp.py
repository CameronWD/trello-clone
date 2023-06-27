from flask import Blueprint, request, abort
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity
from models.user import User, UserSchema
from init import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/users')
def all_users():
    stmt = db.select(User)
    users = db.session.scalars(stmt)
    return UserSchema(many=True, exclude=['password']).dump(users)

@auth_bp.route("/register", methods=['POST'])
def register():
    try:
        # Parse, sanitize and validate the incoming JSON data via the schema
        user_info = UserSchema().load(request.json) #used to santize the data thru marshmallow. Loads the data from the request in the model of the Schema.
        # Create a new user model instance with the same schema
        user = User(
            email=user_info['email'],
            password=bcrypt.generate_password_hash(user_info['password']).decode('utf-8'),
            name=user_info['name']
        )

        # add and commit the new user
        db.session.add(user)
        db.session.commit() #adding the transient user data to the db
        # print(user.__dict__)

        # Return the new user, exclude pw
        return UserSchema(exclude=['password']).dump(user), 201 #important to return the data that was sent but not sensitive information like pw. 201 is because its a creation
    except IntegrityError:
        return{'error': 'Email address already in use'}, 409

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json['email']) #cna use a where statment too. .where but uses a == as boolean
        user = db.session.scalar(stmt) #because scalar is singular, it will only return 1 item/first
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
             #works left ot right. if user isnt 'truthy' will go straight to the else 
            token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))  #expiry delta for the time the token works for
            return {'token': token, 'user': UserSchema(exclude=['password', 'cards']).dump(user)}
        else:
            return {'error': 'Invalid email address or password'}, 401
    except KeyError:
        return {'error': 'Email and password are required.'}, 400
    

def admin_required():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        abort(401)

def admin_or_owner_required(owner_id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not (user and (user.is_admin or user_id == owner_id)):
        abort(401)
    
