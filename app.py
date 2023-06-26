from flask import Flask, request, abort
# from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
# from flask_marshmallow import Marshmallow
# from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from os import environ
from dotenv import load_dotenv
from models.user import User, UserSchema
from models.card import Card, CardSchema
from init import db, ma, bcrypt, jwt
from blueprints.cli_bp import cli_bp
from blueprints.auth_bp import auth_bp
from blueprints.cards_bp import cards_bp



load_dotenv() # will be removed when refactored


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = environ.get('JWT_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get('DB_URI')

# db = SQLAlchemy(app)
# ma = Marshmallow(app)
# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)

db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

def admin_required():
    user_email = get_jwt_identity()
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        abort(401)

@app.errorhandler(401)
def unauthorized(err):
    return{'error': 'You must be an admin'}, 401

app.register_blueprint(cli_bp)

app.register_blueprint(auth_bp)

app.register_blueprint(cards_bp)


@app.route("/")
def index():
    return "Hello World!"

# class Card(db.Model):
#     __tablename__ = "cards"

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     description = db.Column(db.Text())
#     status = db.Column(db.String(30))
#     date_created = db.Column(db.Date())

# class CardSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'title', 'description', 'status')

# class User(db.Model):
#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     email = db.Column(db.String, nullable=False, unique=True)
#     password = db.Column(db.String, nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)

# class UserSchema(ma.Schema):
#     class Meta:
#         fields = ('name', 'email', 'password', 'is_admin')

# @app.cli.command("create")
# def create_db():
#     db.drop_all()
#     db.create_all()
#     print("Tables created successfully")


# @app.cli.command("seed")
# def seed_db():
#     users = [
#         # store user pw as a base 64 string to save space. done using the .decode and specifying what encoding ('utf-8') for example.
#         User(
#             email='admin@spam.com',
#             password=bcrypt.generate_password_hash('spinynorman').decode('utf-8'),
#             is_admin=True
#         ),
#         User(
#             name='John Cleese',
#             email='cleese@spam.com',
#             password=bcrypt.generate_password_hash('tisbutascratch').decode('utf-8')
#         )
#     ]
#     # Create an instance of the Card model in memory
#     cards = [
#         Card(
#             title="Start the project",
#             description="Stage 1 - Create an ERD",
#             status="Done",
#             date_created=date.today(),
#         ),
#         Card(
#             title="ORM Queries",
#             description="Stage 2 - Implement several queries",
#             status="In Progress",
#             date_created=date.today(),
#         ),
#         Card(
#             title="Marshmallow",
#             description="Stage 3 - Implement jsonify of models",
#             status="In Progress",
#             date_created=date.today(),
#         ),
#     ]

#     # Truncate the Card table
#     db.session.query(Card).delete()
#     db.session.query(User).delete()

#     # Add the card to the session (transaction)
#     db.session.add_all(cards)
#     db.session.add_all(users)

#     # Commit the transaction to the database
#     db.session.commit()
#     print("Models seeded")


# @app.route('/cards')
# def all_cards():
#   # select * from cards;
#   stmt = db.select(Card).order_by(Card.status.desc())
#   cards = db.session.scalars(stmt).all()
#   return CardSchema(many=True).dump(cards)

# @app.route('/cards')
# def all_cards():
#    # select * from cards;
#    stmt = db.select(Card).where(db.or_(Card.status != 'Done', Card.id > 2)).order_by(Card.title.desc())
#    # is and by default. Adding the .or_ makes it an or. order by defaults to ascending order. can use a method to change.
#    cards = db.session.scalars(stmt).all()
#    for card in cards:
#       print(card.__dict__)



# @app.route("/register", methods=['POST'])
# def register():
#     try:
#         # Parse, sanitize and validate the incoming JSON data via the schema
#         user_info = UserSchema().load(request.json) #used to santize the data thru marshmallow. Loads the data from the request in the model of the Schema.
#         # Create a new user model instance with the same schema
#         user = User(
#             email=user_info['email'],
#             password=bcrypt.generate_password_hash(user_info['password']).decode('utf-8'),
#             name=user_info['name']
#         )

#         # add and commit the new user
#         db.session.add(user)
#         db.session.commit() #adding the transient user data to the db
#         # print(user.__dict__)

#         # Return the new user, exclude pw
#         return UserSchema(exclude=['password']).dump(user), 201 #important to return the data that was sent but not sensitive information like pw. 201 is because its a creation
#     except IntegrityError:
#         return{'error': 'Email address already in use'}, 409

# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         stmt = db.select(User).filter_by(email=request.json['email']) #cna use a where statment too. .where but uses a == as boolean
#         user = db.session.scalar(stmt) #because scalar is singular, it will only return 1 item/first
#         if user and bcrypt.check_password_hash(user.password, request.json['password']):
#              #works left ot right. if user isnt 'truthy' will go straight to the else 
#             token = create_access_token(identity=user.email, expires_delta=timedelta(days=1))  #expiry delta for the time the token works for
#             return {'token': token, 'user': UserSchema(exclude=['password']).dump(user)}
#         else:
#             return {'error': 'Invalid email address or password'}, 401
#     except KeyError:
#         return {'error': 'Email and password are required.'}, 400

# @app.route('/cards')
# @jwt_required()
# #is possible to make own decorator such as 'admin required'
# def all_cards():
#    admin_required()

# #    user_email = get_jwt_identity()
# #    stmt = db.select(User).filter_by(email=user_email)
# #    user = db.session.scalar(stmt)
# #    if not user.is_admin:
# #        return {'error': 'You musdt be an admin'}, 401
#    # above section checks if the user is an admin. gets the token from login, gets the email, checks that against the is admin and if not an admin, returns error.
#    # select * from cards;
#    stmt = db.select(Card).order_by(Card.status.desc())
#    cards = db.session.scalars(stmt).all()
#    return CardSchema(many=True).dump(cards)

#if using .all on cards, need to set cardschema "many=True"

if __name__ == "__main__":
    app.run(debug=True)