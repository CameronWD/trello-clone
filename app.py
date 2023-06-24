from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://trello_dev:spameggs123@localhost:5432/trello"

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())

class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'status')

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'email', 'password', 'is_admin')

@app.cli.command("create")
def create_db():
    db.drop_all()
    db.create_all()
    print("Tables created successfully")


@app.cli.command("seed")
def seed_db():
    users = [
        # store user pw as a base 64 string to save space. done using the .decode and specifying what encoding ('utf-8') for example.
        User(
            email='admin@spam.com',
            password=bcrypt.generate_password_hash('spinynorman').decode('utf-8'),
            is_admin=True
        ),
        User(
            name='John Cleese',
            email='cleese@spam.com',
            password=bcrypt.generate_password_hash('tisbutascratch').decode('utf-8')
        )
    ]
    # Create an instance of the Card model in memory
    cards = [
        Card(
            title="Start the project",
            description="Stage 1 - Create an ERD",
            status="Done",
            date_created=date.today(),
        ),
        Card(
            title="ORM Queries",
            description="Stage 2 - Implement several queries",
            status="In Progress",
            date_created=date.today(),
        ),
        Card(
            title="Marshmallow",
            description="Stage 3 - Implement jsonify of models",
            status="In Progress",
            date_created=date.today(),
        ),
    ]

    # Truncate the Card table
    db.session.query(Card).delete()
    db.session.query(User).delete()

    # Add the card to the session (transaction)
    db.session.add_all(cards)
    db.session.add_all(users)

    # Commit the transaction to the database
    db.session.commit()
    print("Models seeded")


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

@app.route("/")
def index():
    return "Hello World!"

@app.route("/register", methods=['POST'])
def register():
    user_info = UserSchema().load(request.json) #used to santize the data thru marshmallow
    user = User(
        email=user_info['email'],
        password=bcrypt.generate_password_hash(user_info['password']).decode('utf-8'),
        name=user_info['name']
    )

    db.session.add(user)
    db.session.commit() #adding the transient user data to the db
    # print(user.__dict__)

    return UserSchema(exclude=['password']).dump(user), 201 #important to return the data that was sent but not sensitive information like pw

@app.route('/cards')
def all_cards():
   # select * from cards;
   stmt = db.select(Card).order_by(Card.status.desc())
   cards = db.session.scalars(stmt).all()
   return CardSchema(many=True).dump(cards)

#if using .all on cards, need to set cardschema "many=True"

if __name__ == "__main__":
    app.run(debug=True)