from pydantic import BaseModel, Field
from typing import Optional, List, UUID4
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
    id: UUID4
    purchase_order_id: UUID4
    approved_by: UUID4
    role: str
    approved_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID4
    requested_by: UUID4
    status: PurchaseOrderStatus
    created_at: datetime
    approvals: Optional[List[ApprovalResponse]] = []
    
    class Config:
        orm_mode = True
        from_attributes = True