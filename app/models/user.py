from sqlalchemy import Column, String, Boolean, Enum, Float, Text, ForeignKey, Integer
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum
import uuid

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    SPECIALIST = "specialist"
    MANAGER = "manager"
    DEPUTY_MD = "deputy_md"
    MD = "md"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    description = Column(Text)
    vendor_name = Column(String, nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    
    # Relationships
    requester = relationship("User", back_populates="purchase_orders")
    approvals = relationship("Approval", back_populates="purchase_order")


class ApprovalStatus(str, enum.Enum):
    APPROVED = "approved"
    DENIED = "denied"


class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False)
    comments = Column(Text)
    approved_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")