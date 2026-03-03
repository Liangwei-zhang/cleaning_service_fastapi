from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Text
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Try to import PostGIS types, fallback to basic types if not available
try:
    from geoalchemy2 import Geometry
    HAS_POSTGIS = True
except ImportError:
    HAS_POSTGIS = False


class Cleaner(SQLModel, table=True):
    __tablename__ = "cleaners"
    __table_args__ = (
        Index("idx_cleaner_phone", "phone"),
        Index("idx_cleaner_status", "status"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    password_hash: Optional[str] = None
    status: str = "active"
    # Location (for nearby search)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Host(SQLModel, table=True):
    __tablename__ = "hosts"
    __table_args__ = (
        Index("idx_host_phone", "phone"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    password_hash: Optional[str] = None
    code: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    __table_args__ = (
        Index("idx_property_host_phone", "host_phone"),
        Index("idx_property_status", "status"),
        Index("idx_property_city", "city"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    address: str
    bedrooms: int = 2
    bathrooms: int = 1
    cleaning_time_minutes: int = 120
    host_phone: str = ""
    province: str = ""
    city: str = ""
    street: str = ""
    house_number: str = ""
    postal_code: str = ""
    floor: int = 0
    area: float = 0.0
    # Location (for nearby search)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "active"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_order_property_id", "property_id"),
        Index("idx_order_status", "status"),
        Index("idx_order_cleaner_id", "assigned_cleaner_id"),
        Index("idx_order_checkout_time", "checkout_time"),
        Index("idx_order_created_at", "created_at"),
        Index("idx_order_host_phone", "host_phone"),
        Index("idx_order_status_checkout", "status", "checkout_time"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int
    host_name: str = ""
    host_phone: str = ""
    checkout_time: str
    price: float = 100.0
    status: str = "open"
    assigned_cleaner_id: Optional[int] = None
    assigned_at: Optional[str] = None
    arrived_at: Optional[str] = None
    voice_url: Optional[str] = None
    text_notes: Optional[str] = None
    completion_photos: Optional[str] = None
    accepted_by_host: int = 0
    host_id: Optional[int] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
