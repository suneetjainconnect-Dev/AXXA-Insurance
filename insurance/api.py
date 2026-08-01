from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'axxa_insurance.settings')

import django
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from insurance.models import Customer, Policy, Claim, Document, Notification

app = FastAPI(title="AXXA Insurance API", description="API for AXXA Insurance Management System")

security = HTTPBasic()

# ==================== Pydantic Models ====================

class UserBase(BaseModel):
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""

class UserCreate(UserBase):
    password: str

class CustomerBase(BaseModel):
    phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    date_of_birth: Optional[date] = None
    gender: str = ""

class CustomerOut(CustomerBase):
    user: UserBase

class PolicyBase(BaseModel):
    policy_type: str
    start_date: date
    end_date: date
    premium_amount: float
    coverage_amount: float
    status: str = "draft"

class PolicyOut(PolicyBase):
    id: int
    policy_number: str
    customer: UserBase

class ClaimBase(BaseModel):
    claim_type: str
    description: str
    incident_date: date
    claim_amount: float

class ClaimOut(ClaimBase):
    id: int
    claim_number: str
    policy: int
    customer: UserBase
    status: str
    processed_amount: float
    submitted_at: str

class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str
    priority: str = "medium"

class NotificationOut(NotificationBase):
    id: int
    customer: UserBase
    is_read: bool

class LoginRequest(BaseModel):
    username: str
    password: str

# ==================== Helper Functions ====================

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate(username=credentials.username, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def get_current_customer(user: User = Depends(authenticate_user)):
    try:
        return user.customer
    except Customer.DoesNotExist:
        raise HTTPException(status_code=400, detail="Customer profile not found")

# ==================== Auth Endpoints ====================

@app.post("/api/login", tags=["Authentication"])
def login(request: LoginRequest):
    user = authenticate(username=request.username, password=request.password)
    if user:
        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/register", tags=["Authentication"])
def register(request: UserCreate):
    if User.objects.filter(username=request.username).exists():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = User.objects.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    return {"message": "User created successfully", "user_id": user.id}

# ==================== Customer Endpoints ====================

@app.get("/api/customers/me", tags=["Customers"])
def get_current_customer_profile(customer: Customer = Depends(get_current_customer)):
    return {
        "user": {
            "id": customer.user.id,
            "username": customer.user.username,
            "email": customer.user.email,
            "first_name": customer.user.first_name,
            "last_name": customer.user.last_name
        },
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "zip_code": customer.zip_code,
        "date_of_birth": customer.date_of_birth,
        "gender": customer.gender
    }

@app.put("/api/customers/me", tags=["Customers"])
def update_customer_profile(profile: CustomerBase, customer: Customer = Depends(get_current_customer)):
    for field, value in profile.model_dump().items():
        setattr(customer, field, value)
    customer.save()
    return {"message": "Profile updated successfully", "customer": customer}

# ==================== Policy Endpoints ====================

@app.get("/api/policies", tags=["Policies"])
def list_policies(customer: Customer = Depends(get_current_customer)):
    policies = Policy.objects.filter(customer=customer)
    return [
        {
            "id": policy.id,
            "policy_number": policy.policy_number,
            "policy_type": policy.policy_type,
            "start_date": policy.start_date,
            "end_date": policy.end_date,
            "premium_amount": str(policy.premium_amount),
            "coverage_amount": str(policy.coverage_amount),
            "status": policy.status
        }
        for policy in policies
    ]

@app.get("/api/policies/{policy_id}", tags=["Policies"])
def get_policy(policy_id: int, customer: Customer = Depends(get_current_customer)):
    try:
        policy = Policy.objects.get(id=policy_id, customer=customer)
        return {
            "id": policy.id,
            "policy_number": policy.policy_number,
            "policy_type": policy.policy_type,
            "provider_name": policy.provider_name,
            "start_date": policy.start_date,
            "end_date": policy.end_date,
            "premium_amount": str(policy.premium_amount),
            "coverage_amount": str(policy.coverage_amount),
            "status": policy.status
        }
    except Policy.DoesNotExist:
        raise HTTPException(status_code=404, detail="Policy not found")

@app.post("/api/policies", tags=["Policies"])
def create_policy(policy: PolicyBase, customer: Customer = Depends(get_current_customer)):
    policy_obj = Policy.objects.create(
        customer=customer,
        policy_type=policy.policy_type,
        start_date=policy.start_date,
        end_date=policy.end_date,
        premium_amount=policy.premium_amount,
        coverage_amount=policy.coverage_amount,
        status=policy.status
    )
    return {"message": "Policy created successfully", "policy_id": policy_obj.id}

# ==================== Claim Endpoints ====================

@app.get("/api/claims", tags=["Claims"])
def list_claims(customer: Customer = Depends(get_current_customer)):
    claims = Claim.objects.filter(customer=customer)
    return [
        {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "claim_type": claim.claim_type,
            "policy": claim.policy.id,
            "description": claim.description,
            "incident_date": claim.incident_date,
            "claim_amount": str(claim.claim_amount),
            "status": claim.status,
            "processed_amount": str(claim.processed_amount),
            "submitted_at": str(claim.submitted_at)
        }
        for claim in claims
    ]

@app.get("/api/claims/{claim_id}", tags=["Claims"])
def get_claim(claim_id: int, customer: Customer = Depends(get_current_customer)):
    try:
        claim = Claim.objects.get(id=claim_id, customer=customer)
        return {
            "id": claim.id,
            "claim_number": claim.claim_number,
            "claim_type": claim.claim_type,
            "policy": claim.policy.id,
            "description": claim.description,
            "incident_date": claim.incident_date,
            "claim_amount": str(claim.claim_amount),
            "status": claim.status,
            "processed_amount": str(claim.processed_amount),
            "rejected_reason": claim.rejection_reason,
            "submitted_at": str(claim.submitted_at)
        }
    except Claim.DoesNotExist:
        raise HTTPException(status_code=404, detail="Claim not found")

@app.post("/api/policies/{policy_id}/claims", tags=["Claims"])
def create_claim(policy_id: int, claim: ClaimBase, customer: Customer = Depends(get_current_customer)):
    try:
        policy = Policy.objects.get(id=policy_id, customer=customer)
        claim_obj = Claim.objects.create(
            policy=policy,
            customer=customer,
            claim_type=claim.claim_type,
            description=claim.description,
            incident_date=claim.incident_date,
            claim_amount=claim.claim_amount,
            claim_number=f"CLM-{policy.id}-{Claim.objects.filter(policy=policy).count() + 1}"
        )
        return {"message": "Claim created successfully", "claim_id": claim_obj.id}
    except Policy.DoesNotExist:
        raise HTTPException(status_code=404, detail="Policy not found")

@app.put("/api/claims/{claim_id}", tags=["Claims"])
def update_claim_status(claim_id: int, status_update: dict, customer: Customer = Depends(get_current_customer)):
    try:
        claim = Claim.objects.get(id=claim_id, customer=customer)
        new_status = status_update.get("status")
        if new_status and new_status in dict(Claim.STATUS_CHOICES):
            claim.status = new_status
            claim.save()
        return {"message": "Claim updated successfully", "claim_id": claim.id, "status": claim.status}
    except Claim.DoesNotExist:
        raise HTTPException(status_code=404, detail="Claim not found")

# ==================== Notification Endpoints ====================

@app.get("/api/notifications", tags=["Notifications"])
def list_notifications(customer: Customer = Depends(get_current_customer)):
    notifications = Notification.objects.filter(customer=customer)
    return [
        {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "notification_type": notif.notification_type,
            "priority": notif.priority,
            "is_read": notif.is_read,
            "created_at": str(notif.created_at)
        }
        for notif in notifications
    ]

@app.put("/api/notifications/{notif_id}/read", tags=["Notifications"])
def mark_notification_read(notif_id: int, customer: Customer = Depends(get_current_customer)):
    try:
        notification = Notification.objects.get(id=notif_id, customer=customer)
        notification.is_read = True
        notification.save()
        return {"message": "Notification marked as read", "notif_id": notification.id}
    except Notification.DoesNotExist:
        raise HTTPException(status_code=404, detail="Notification not found")

# ==================== Premium Calculator ====================

@app.get("/api/calculate-premium", tags=["Calculator"])
def calculate_premium(policy_type: str, coverage_amount: float, age: int):
    base_rates = {
        "health": 5000,
        "life": 3000,
        "motor": 8000,
        "home": 4000,
        "travel": 2000,
        "business": 15000,
    }
    
    rate = base_rates.get(policy_type.lower(), 0)
    premium = rate + (coverage_amount * 0.01) + (age * 50)
    
    return {
        "policy_type": policy_type,
        "coverage_amount": coverage_amount,
        "age": age,
        "estimated_premium": premium,
        "currency": "USD"
    }
