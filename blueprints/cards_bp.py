from flask import Blueprint
from flask_jwt_extended import jwt_required
from models.card import Card, CardSchema
from init import db

cards_bp = Blueprint('cards', __name__)
@app.route('/cards')
@jwt_required()
#is possible to make own decorator such as 'admin required'
def all_cards():
   admin_required()

#    user_email = get_jwt_identity()
#    stmt = db.select(User).filter_by(email=user_email)
#    user = db.session.scalar(stmt)
#    if not user.is_admin:
#        return {'error': 'You musdt be an admin'}, 401
   # above section checks if the user is an admin. gets the token from login, gets the email, checks that against the is admin and if not an admin, returns error.
   # select * from cards;
   stmt = db.select(Card).order_by(Card.status.desc())
   cards = db.session.scalars(stmt).all()
   return CardSchema(many=True).dump(cards)
