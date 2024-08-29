ls
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    close = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<StockData {self.ticker} on {self.date}>'
