from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.card import Card, CardSchema
from init import db
from blueprints.auth_bp import admin_required, admin_or_owner_required
from datetime import date


cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

# Get all cards
@cards_bp.route('/')
@jwt_required()
def all_cards():
   admin_required()

   # select * from cards;
   stmt = db.select(Card).order_by(Card.status.desc())
   cards = db.session.scalars(stmt).all()
   return CardSchema(many=True).dump(cards)

# Get one card
@cards_bp.route('/<int:card_id>')
@jwt_required()
def one_card(card_id):
   stmt = db.select(Card).filter_by(id=card_id)
   card = db.session.scalar(stmt)
   if card:
   # if card is truthy aka there is a card. 
      return CardSchema().dump(card)
   else:
      return{'error': 'Card not found'}, 404

# Create a new card
@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_card():
     # Load the incoming POST data via the schema
     # Should be in a try except incase wrong info is provided
     # Technically should get JWT identity first and CHECK user exissts before creating card.
     # In the case that an admin  has deleted the user while they are logged in.  
     card_info = CardSchema().load(request.json)
     # Create a new Card instance from the card_info
     card = Card(
        title = card_info['title'],
        description = card_info['description'],
        status = card_info['status'],
        date_created = date.today(),
        user_id = get_jwt_identity()
     )
     # Can store the date using linux epochs 
     # Add and commit the new card to the session
     db.session.add(card)
     db.session.commit()
     # Send the new card back to the client
     return CardSchema().dump(card), 201

# Update a card
@cards_bp.route('/<int:card_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_card(card_id):
   stmt = db.select(Card).filter_by(id=card_id)
   card = db.session.scalar(stmt)
   card_info = CardSchema().load(request.json)
   if card:
      admin_or_owner_required(card.user.id)
      card.title = card_info.get('title', card.title)
      card.description = card_info.get('description', card.description)
      card.status = card_info.get('status', card.status)
      # the get method lets us provide a default value incase key value not provided
      db.session.commit()
      return CardSchema().dump(card)
   else:
      return {'error': 'Card not found'}, 404
   
# Delete a card
@cards_bp.route('/<int:card_id>', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
   stmt = db.select(Card).filter_by(id=card_id)
   card = db.session.scalar(stmt)
   if card:
      admin_or_owner_required(card.user.id)
      db.session.delete(card)
      db.session.commit()
      return {}, 200
   else:
      return{'error': 'Card not found'}, 404