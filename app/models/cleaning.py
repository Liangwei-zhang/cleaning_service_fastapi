from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Cleaner(SQLModel, table=True):
    __tablename__ = "cleaners"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    status: str = "active"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Host(SQLModel, table=True):
    __tablename__ = "hosts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    code: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    
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
    status: str = "active"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
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
