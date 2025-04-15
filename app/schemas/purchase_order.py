from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID  # Change from UUID4 to UUID
from datetime import datetime
from app.models.user import PurchaseOrderStatus, ApprovalStatus, UserRole

class PurchaseOrderBase(BaseModel):
    item_name: str
    quantity: int
    cost: float
    description: Optional[str] = None
    vendor_name: str

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class ApprovalBase(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalResponse(ApprovalBase):
    id: UUID
    purchase_order_id: UUID
    approved_by: UUID
    role: str
    approved_at: datetime
    
    class Config:
        from_attributes = True  # Remove orm_mode

class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID
    requested_by: UUID
    status: PurchaseOrderStatus
    created_at: datetime
    approvals: Optional[List[ApprovalResponse]] = []
    
    class Config:
        from_attributes = True  # Remove orm_mode