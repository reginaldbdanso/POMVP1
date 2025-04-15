from sqlalchemy import Column, String, Boolean, Enum, Float, Text, ForeignKey, Integer, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum
import uuid

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    SPECIALIST = "specialist"
    MANAGER = "manager"
    DEPUTY_MD = "deputy_md"
    MD = "md"
    ADMIN = "admin" 

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="requester")
    approvals = relationship("Approval", back_populates="approver")


class PurchaseOrderStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    AWAITING_MD = "awaiting_md"
    AWAITING_DEPUTY_MD = "awaiting_deputy_md"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost = Column(Float(precision=10), nullable=False)  # Remove 'scale' parameter
    description = Column(Text)
    vendor_name = Column(String(100), nullable=False)
    requested_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    requester = relationship("User", back_populates="purchase_orders")
    approvals = relationship("Approval", back_populates="purchase_order")


class ApprovalStatus(str, enum.Enum):
    APPROVED = "approved"
    DENIED = "denied"


class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False)
    comments = Column(Text)
    approved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")