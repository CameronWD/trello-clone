from flask import Blueprint
from datetime import date
from init import db, bcrypt
from models.user import User
from models.card import Card

cli_bp = Blueprint('db', __name__)

@cli_bp.cli.command("create")
def create_db():
    db.drop_all()
    db.create_all()
    print("Tables created successfully")


@cli_bp.cli.command("seed")
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
    db.session.query(User).delete()
    db.session.add_all(users)
    db.session.commit()
    # Create an instance of the Card model in memory
    cards = [
        Card(
            title="Start the project",
            description="Stage 1 - Create an ERD",
            status="Done",
            date_created=date.today(),
            user_id=users[0].id
        ),
        Card(
            title="ORM Queries",
            description="Stage 2 - Implement several queries",
            status="In Progress",
            date_created=date.today(),
            user_id=users[0].id
        ),
        Card(
            title="Marshmallow",
            description="Stage 3 - Implement jsonify of models",
            status="In Progress",
            date_created=date.today(),
            user_id=users[1].id
        ),
    ]

    # Truncate the Card table
    db.session.query(Card).delete()
    db.session.add_all(cards)
    db.session.commit()


    # Add the card to the session (transaction)
    


    # Commit the transaction to the database
    db.session.commit()
    print("Models seeded")