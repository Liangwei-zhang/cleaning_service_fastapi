from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import select, func
from typing import List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta

from app.models.cleaning import Cleaner, Host, Property, Order
from app.core.database import get_session
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_active_cleaner, get_current_active_host
)
from app.services.cache import cache, CacheKeys
from app.services.lock import OrderLock, lock_manager
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["api"])


# ========== Auth ==========
@router.post("/auth/login")
def login(data: dict, session: Session = Depends(get_session)):
    """Login with phone and password, returns JWT token"""
    phone = data.get("phone", "")
    password = data.get("password", "")
    user_type = data.get("type", "cleaner")  # cleaner or host
    
    # Find user
    if user_type == "cleaner":
        statement = select(Cleaner).where(Cleaner.phone == phone)
    else:
        statement = select(Host).where(Host.phone == phone)
    
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.id, "type": user_type},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "type": user_type
        }
    }


@router.post("/auth/register")
def register(data: dict, session: Session = Depends(get_session)):
    """Register new user"""
    phone = data.get("phone", "")
    password = data.get("password", "")
    name = data.get("name", "")
    user_type = data.get("type", "cleaner")
    
    if not phone or not password:
        raise HTTPException(status_code=400, detail="Phone and password required")
    
    # Check if user exists
    if user_type == "cleaner":
        statement = select(Cleaner).where(Cleaner.phone == phone)
    else:
        statement = select(Host).where(Host.phone == phone)
    
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user with hashed password
    password_hash = get_password_hash(password)
    
    if user_type == "cleaner":
        user = Cleaner(name=name, phone=phone, password_hash=password_hash, status="active")
    else:
        user = Host(name=name, phone=phone, password_hash=password_hash, code=phone)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.id, "type": user_type},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "type": user_type
        }
    }


@router.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# ========== Cleaners ==========
@router.get("/cleaners")
def get_cleaners(session: Session = Depends(get_session)):
    """Get all cleaners"""
    # Try cache first
    cached = cache.get(CacheKeys.CLEANERS)
    if cached:
        return {"data": cached}
    
    statement = select(Cleaner)
    results = session.exec(statement).all()
    data = [r.dict() for r in results]
    
    # Cache for 5 minutes
    cache.set(CacheKeys.CLEANERS, data, ttl=300)
    
    return {"data": data}


@router.post("/cleaners")
def add_cleaner(data: dict, session: Session = Depends(get_session)):
    """Add new cleaner"""
    cleaner = Cleaner(
        name=data.get("name", ""),
        phone=data.get("phone", ""),
        status=data.get("status", "active")
    )
    session.add(cleaner)
    session.commit()
    session.refresh(cleaner)
    cache_clear("cleaners")
    return {"data": {"id": cleaner.id}}


@router.delete("/cleaners/{cleaner_id}")
def delete_cleaner(cleaner_id: int, session: Session = Depends(get_session)):
    """Delete cleaner"""
    cleaner = session.get(Cleaner, cleaner_id)
    if not cleaner:
        raise HTTPException(status_code=404, detail="Cleaner not found")
    session.delete(cleaner)
    session.commit()
    cache_clear("cleaners")
    return {"message": "Deleted"}


# ========== Hosts ==========
@router.post("/hosts/login")
def host_login(data: dict, session: Session = Depends(get_session)):
    """Host login by phone"""
    phone = data.get("phone", "")
    code = data.get("code", "")
    
    statement = select(Host).where(Host.phone == phone)
    host = session.exec(statement).first()
    
    if host:
        return {"data": {"id": host.id, "name": host.name, "phone": host.phone}}
    
    # Create new host
    new_host = Host(name=data.get("name", ""), phone=phone, code=code)
    session.add(new_host)
    session.commit()
    session.refresh(new_host)
    return {"data": {"id": new_host.id, "name": new_host.name, "phone": new_host.phone}}


@router.post("/hosts/login-by-code")
def host_login_by_code(data: dict, session: Session = Depends(get_session)):
    """Host login by code"""
    code = data.get("code", "")
    statement = select(Host).where(Host.code == code)
    host = session.exec(statement).first()
    
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return {"data": {"id": host.id, "name": host.name, "phone": host.phone}}


@router.get("/hosts")
def get_hosts(session: Session = Depends(get_session)):
    """Get all hosts"""
    statement = select(Host)
    results = session.exec(statement).all()
    return {"data": [r.dict() for r in results]}


@router.get("/hosts/code/{code}")
def get_host_by_code(code: str, session: Session = Depends(get_session)):
    """Get host by code"""
    statement = select(Host).where(Host.code == code)
    host = session.exec(statement).first()
    if host:
        return {"data": {"id": host.id, "name": host.name, "phone": host.phone, "code": host.code}}
    return {"data": None}


@router.post("/hosts")
def add_host(data: dict, session: Session = Depends(get_session)):
    """Add new host"""
    host = Host(
        name=data.get("name", ""),
        phone=data.get("phone", ""),
        code=data.get("code", "")
    )
    session.add(host)
    session.commit()
    session.refresh(host)
    return {"data": {"id": host.id}}


# ========== Properties ==========
@router.get("/properties")
def get_properties(
    host_phone: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get properties"""
    if host_phone:
        statement = select(Property).where(Property.host_phone == host_phone)
    else:
        statement = select(Property)
    results = session.exec(statement).all()
    return {"data": [r.dict() for r in results]}


@router.get("/properties/{property_id}")
def get_property(property_id: int, session: Session = Depends(get_session)):
    """Get single property"""
    prop = session.get(Property, property_id)
    if prop:
        return {"data": prop.dict()}
    return {"data": None}


@router.post("/properties")
def add_property(data: dict, session: Session = Depends(get_session)):
    """Add new property"""
    property = Property(
        name=data.get("name", ""),
        address=data.get("address", ""),
        host_phone=data.get("host_phone", ""),
        province=data.get("province", ""),
        city=data.get("city", ""),
        street=data.get("street", ""),
        house_number=data.get("house_number", ""),
        postal_code=data.get("postal_code", ""),
        floor=data.get("floor", 0),
        area=data.get("area", 0.0)
    )
    session.add(property)
    session.commit()
    session.refresh(property)
    cache_clear("properties")
    return {"data": {"id": property.id}}


@router.put("/properties/{property_id}")
def update_property(property_id: int, data: dict, session: Session = Depends(get_session)):
    """Update property"""
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    for key, value in data.items():
        if hasattr(property, key):
            setattr(property, key, value)
    
    session.commit()
    cache_clear("properties")
    return {"data": property.dict()}


@router.delete("/properties/{property_id}")
def delete_property(property_id: int, session: Session = Depends(get_session)):
    """Delete property"""
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    session.delete(property)
    session.commit()
    cache_clear("properties")
    return {"message": "Deleted"}


# ========== Orders ==========
@router.get("/orders")
def get_orders(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Get orders with pagination"""
    # Count total
    count_stmt = select(func.count(Order.id))
    if status:
        count_stmt = count_stmt.where(Order.status == status)
    total = session.exec(count_stmt).one()
    
    # Get data
    offset = (page - 1) * limit
    statement = select(Order).offset(offset).limit(limit)
    if status:
        statement = statement.where(Order.status == status)
    results = session.exec(statement).all()
    
    # Enrich with property info
    data = []
    for r in results:
        order_dict = r.model_dump()
        if r.property_id:
            prop = session.get(Property, r.property_id)
            if prop:
                order_dict["property_name"] = prop.name
                order_dict["property_address"] = prop.address
                order_dict["property_street"] = prop.street
                order_dict["property_city"] = prop.city
                order_dict["property_province"] = prop.province
                order_dict["property_house_number"] = prop.house_number
        data.append(order_dict)
    
    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.post("/orders")
def create_order(data: dict, session: Session = Depends(get_session)):
    """Create new order"""
    order = Order(
        property_id=data.get("property_id"),
        host_name=data.get("host_name", ""),
        host_phone=data.get("host_phone", ""),
        checkout_time=data.get("checkout_time"),
        price=data.get("price", 100),
        status="open",
        voice_url=data.get("voice_url"),
        text_notes=data.get("text_notes")
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    cache_clear("orders")
    return {"data": {"id": order.id}}


@router.get("/orders/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)):
    """Get order by ID"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"data": order.dict()}


@router.put("/orders/{order_id}")
def update_order(order_id: int, data: dict, session: Session = Depends(get_session)):
    """Update order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for key, value in data.items():
        if hasattr(order, key):
            setattr(order, key, value)
    
    session.commit()
    cache_clear("orders")
    return {"data": order.dict()}


@router.post("/orders/{order_id}/accept")
def accept_order(order_id: int, data: dict, session: Session = Depends(get_session)):
    """Accept/order by cleaner with distributed lock"""
    # Use distributed lock to prevent race condition
    try:
        with OrderLock(order_id, timeout=10):
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            if order.status != "open":
                raise HTTPException(status_code=400, detail="Order not available")
            
            cleaner_id = data.get("cleaner_id")
            order.assigned_cleaner_id = cleaner_id
            order.status = "accepted"
            order.assigned_at = datetime.now().isoformat()
            
            session.commit()
            cache_clear("orders")
            return {"data": order.dict()}
    except Exception as e:
        if "Failed to acquire lock" in str(e):
            raise HTTPException(status_code=409, detail="Order is being processed, please try again")
        raise


@router.post("/orders/{order_id}/arrived")
def arrived_order(order_id: int, session: Session = Depends(get_session)):
    """Mark cleaner arrived"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.arrived_at = datetime.now().isoformat()
    session.commit()
    return {"data": order.dict()}


@router.post("/orders/{order_id}/complete")
def complete_order(order_id: int, data: dict, session: Session = Depends(get_session)):
    """Complete order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "completed"
    order.completion_photos = json.dumps(data.get("photos", []))
    
    session.commit()
    cache_clear("orders")
    return {"data": order.dict()}


@router.post("/orders/{order_id}/verify-accept")
def verify_accept_order(order_id: int, session: Session = Depends(get_session)):
    """Verify and accept by host"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.accepted_by_host = 1
    session.commit()
    return {"data": order.dict()}


@router.delete("/orders/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)):
    """Delete order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    cache_clear("orders")
    return {"message": "Deleted"}


# ========== Upload ==========
@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image"""
    import base64
    contents = await file.read()
    
    # Save to file
    filename = f"{uuid.uuid4()}.jpg"
    filepath = f"uploads/images/{filename}"
    
    os.makedirs("uploads/images", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(contents)
    
    return {"url": f"/uploads/images/{filename}"}


@router.post("/upload/voice")
async def upload_voice(file: UploadFile = File(...)):
    """Upload voice"""
    contents = await file.read()
    
    filename = f"{uuid.uuid4()}.webm"
    filepath = f"uploads/voice/{filename}"
    
    os.makedirs("uploads/voice", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(contents)
    
    return {"url": f"/uploads/voice/{filename}"}


# ========== Stats ==========
@router.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    """Get statistics"""
    # Try cache first
    cached = cache.get(CacheKeys.STATS)
    if cached:
        return {"data": cached}
    
    total_orders = session.exec(select(func.count(Order.id))).one()
    pending_orders = session.exec(select(func.count(Order.id)).where(Order.status == "open")).one()
    completed_orders = session.exec(select(func.count(Order.id)).where(Order.status == "completed")).one()
    total_cleaners = session.exec(select(func.count(Cleaner.id))).one()
    total_hosts = session.exec(select(func.count(Host.id))).one()
    
    data = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_cleaners": total_cleaners,
        "total_hosts": total_hosts
    }
    
    # Cache for 1 minute
    cache.set(CacheKeys.STATS, data, ttl=60)
    
    return {"data": data}


def cache_clear(pattern: str):
    """Clear cache"""
    cache.invalidate_pattern(f"*{pattern}*")


# ========== Location-based Search ==========
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km (Haversine formula)"""
    import math
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@router.get("/properties/nearby")
def get_nearby_properties(
    latitude: float,
    longitude: float,
    radius_km: float = 10,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Get properties within radius ( PostGIS-free implementation)"""
    # Get all active properties with location
    statement = select(Property).where(
        Property.status == "active",
        Property.latitude.isnot(None),
        Property.longitude.isnot(None)
    )
    results = session.exec(statement).all()
    
    # Filter by distance
    nearby = []
    for prop in results:
        distance = calculate_distance(latitude, longitude, prop.latitude, prop.longitude)
        if distance <= radius_km:
            nearby.append({
                **prop.dict(),
                "distance_km": round(distance, 2)
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "data": nearby[:limit],
        "total": len(nearby)
    }


@router.get("/cleaners/nearby")
def get_nearby_cleaners(
    latitude: float,
    longitude: float,
    radius_km: float = 10,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Get available cleaners within radius"""
    # Get all active cleaners with location
    statement = select(Cleaner).where(
        Cleaner.status == "active",
        Cleaner.latitude.isnot(None),
        Cleaner.longitude.isnot(None)
    )
    results = session.exec(statement).all()
    
    # Filter by distance
    nearby = []
    for cleaner in results:
        distance = calculate_distance(latitude, longitude, cleaner.latitude, cleaner.longitude)
        if distance <= radius_km:
            nearby.append({
                **cleaner.dict(),
                "distance_km": round(distance, 2)
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "data": nearby[:limit],
        "total": len(nearby)
    }


@router.put("/cleaners/{cleaner_id}/location")
def update_cleaner_location(
    cleaner_id: int,
    data: dict,
    current_user: dict = Depends(get_current_active_cleaner),
    session: Session = Depends(get_session)
):
    """Update cleaner location"""
    if current_user["id"] != cleaner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cleaner = session.get(Cleaner, cleaner_id)
    if not cleaner:
        raise HTTPException(status_code=404, detail="Cleaner not found")
    
    cleaner.latitude = data.get("latitude")
    cleaner.longitude = data.get("longitude")
    
    session.commit()
    
    return {"data": cleaner.dict()}


@router.put("/properties/{property_id}/location")
def update_property_location(
    property_id: int,
    data: dict,
    session: Session = Depends(get_session)
):
    """Update property location"""
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property.latitude = data.get("latitude")
    property.longitude = data.get("longitude")
    
    session.commit()
    
    return {"data": property.dict()}


# ========== Geocode ==========
import httpx
import re

@router.get("/geocode")
async def geocode_address(address: str):
    """Geocode address using Nominatim"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1, "addressdetails": 1},
                headers={"User-Agent": "SmartClean/1.0"},
                timeout=10.0
            )
            data = resp.json()
            if not data:
                return {"success": False, "error": "Address not found"}
            
            result = data[0]
            addr = result.get("address", {})
            
            # Parse display_name for additional info
            display = result.get("display_name", "")
            
            return {
                "success": True,
                "province": addr.get("state", "") or addr.get("province", ""),
                "city": addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality", ""),
                "street": addr.get("road", ""),
                "house_number": addr.get("house_number", ""),
                "postcode": addr.get("postcode", ""),
                "latitude": float(result.get("lat", 0)),
                "longitude": float(result.get("lon", 0)),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
