from sqlalchemy import Column, Integer, Numeric, Text, DateTime, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import DjangoBase

class Game(DjangoBase):
    __tablename__ = 'games_game'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    steam_id = Column(Integer, nullable=True)
    psn_id = Column(String, nullable=True)
    psn_product_id = Column(String, nullable=True)
    eshop_id = Column(Text, nullable=True)
    eshop_url = Column(Text, nullable=True)
    last_synced = Column(DateTime)

class PriceEntry(DjangoBase):
    __tablename__ = 'games_priceentry'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games_game.id'))
    store = Column(Text)
    price = Column(Numeric(8,2), nullable=True)
    currency = Column(Text, default='EUR')
    fetched_at = Column(DateTime)
    is_on_sale = Column(Boolean, default=False)
    url = Column(Text)
    original_price = Column(Numeric(8,2), nullable=True)

    game = relationship('Game')

class PriceHistory(DjangoBase):
    __tablename__ = 'games_pricehistory'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games_game.id'))
    store = Column(Text)
    price = Column(Numeric(8, 2), nullable=True)
    currency = Column(Text, default='EUR')
    recorded_at = Column(DateTime)
    is_on_sale = Column(Boolean, default=False)
    original_price = Column(Numeric(8,2), nullable=True)

    game = relationship('Game')
    
