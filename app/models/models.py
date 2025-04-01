from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class HistoricalPrice(db.Model):
    __tablename__ = 'historical_prices'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    close = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('ticker', 'date', name='unique_ticker_date'),
    )

class SectorData(db.Model):
    __tablename__ = 'sector_data'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    beta = db.Column(db.Float, nullable=False)
    lot_size = db.Column(db.Float, nullable=False)