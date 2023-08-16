from datetime import datetime
from app import db

class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.String(30), nullable=False)
    school_name = db.Column(db.String(255), nullable=False)
    geolocation = db.Column(db.String(255), nullable=False)  # Stored as "latitude,longitude"
    internet_speed = db.Column(db.Float)
    provider = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    data_source = db.Column(db.String(255))

    def __repr__(self):
        return f'<School {self.school_name}>'