from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData,ForeignKey
from sqlalchemy.orm import validates,relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


    # Add relationship
    vendors = relationship('VendorSweet', back_populates='sweet')
    # Add serialization
    vendors_rel = association_proxy('vendors', 'vendor')

    
    def __repr__(self):
        return f'<Sweet {self.id}>'


class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    sweets = relationship('VendorSweet', back_populates='vendor')
    # Add serialization
    sweets_rel = association_proxy('sweets', 'sweet')

    
    def __repr__(self):
        return f'<Vendor {self.id}>'


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Add relationships
    sweet_id = db.Column(db.Integer, ForeignKey('sweets.id', ondelete='CASCADE'), nullable=False)
    sweet = relationship('Sweet', back_populates='vendors')

    # Add serialization
    vendor_id = db.Column(db.Integer, ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)
    vendor = relationship('Vendor', back_populates='sweets')
    
    # Add validation
    @validates('price')
    def validate_price(self, key, price):
        if price is None:
            raise ValueError("Price cannot be None")
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    def __repr__(self):
        return f'<VendorSweet {self.id}>'