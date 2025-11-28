from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # admin, user, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    access_records = relationship("ApiAccess", back_populates="user")

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    api_key = Column(String, unique=True, nullable=False)
    description = Column(Text)
    access_token = Column(String, nullable=True)
    token_ttl = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organizations = relationship("Organization", back_populates="api_key")
    access_records = relationship("ApiAccess", back_populates="api_key")

class ApiAccess(Base):
    __tablename__ = "api_access"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), primary_key=True)
    
    user = relationship("User", back_populates="access_records")
    api_key = relationship("ApiKey", back_populates="access_records")

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    organization_id = Column(String, nullable=False, index=True)
    name = Column(String)

    api_key = relationship("ApiKey", back_populates="organizations")
    terminals = relationship("Terminal", back_populates="organization")
    order_types = relationship("OrderType", back_populates="organization")
    payment_types = relationship("PaymentType", back_populates="organization")
    discount_types = relationship("DiscountType", back_populates="organization")

class Terminal(Base):
    __tablename__ = "terminals"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    terminal_id = Column(String, nullable=False, index=True)
    name = Column(String)

    organization = relationship("Organization", back_populates="terminals")

class OrderType(Base):
    __tablename__ = "order_types"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    order_type_id = Column(String, nullable=False)
    name = Column(String)
    order_service_type = Column(String, nullable=False)

    organization = relationship("Organization", back_populates="order_types")

class PaymentType(Base):
    __tablename__ = "payment_types"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    payment_type_id = Column(String, nullable=False)
    name = Column(String)
    payment_type_kind = Column(String, nullable=False)
    code = Column(String, nullable=False)

    organization = relationship("Organization", back_populates="payment_types")

class DiscountType(Base):
    __tablename__ = "discount_types"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    discount_type_id = Column(String, nullable=False)
    name = Column(String, index=True)

    organization = relationship("Organization", back_populates="discount_types")