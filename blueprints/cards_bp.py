from flask import Blueprint
from flask_jwt_extended import jwt_required
from models.card import Card, CardSchema
from init import db
from blueprints.auth_bp import admin_required


cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/cards')
@jwt_required()
def all_cards():
   admin_required()

   # select * from cards;
   stmt = db.select(Card).order_by(Card.status.desc())
   cards = db.session.scalars(stmt).all()
   return CardSchema(many=True).dump(cards)

@cards_bp.route('/cards/<int:card_id>')
def one_card(card_id):
      stmt = db.select(Card).filter_by(id=card_id)
      card = db.session.scalar(stmt)
      if card:
      # if card is truthy aka there is a card. 
           return CardSchema().dump(card)
      else:
           return{'error': 'Card not found'}, 404
   