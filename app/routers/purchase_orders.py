from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, PurchaseOrder, Approval, PurchaseOrderStatus, ApprovalStatus, UserRole
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderResponse, ApprovalCreate, ApprovalResponse
from app.auth.jwt import get_current_active_user
import uuid

router = APIRouter( redirect_slashes=False )


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    purchase_order: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new purchase order (employees only)"""
    # Only employees and above can create purchase orders
    if current_user.role not in [UserRole.EMPLOYEE, UserRole.SPECIALIST, UserRole.MANAGER, UserRole.DEPUTY_MD, UserRole.MD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can create purchase orders"
        )
    
    # Create new purchase order
    new_purchase_order = PurchaseOrder(
        **purchase_order.dict(),
        requested_by=current_user.id,
        status=PurchaseOrderStatus.PENDING
    )
    
    db.add(new_purchase_order)
    db.commit()
    db.refresh(new_purchase_order)
    
    return new_purchase_order


@router.get("", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get purchase orders based on user role"""
    print(f"User role: {current_user.role}, User ID: {current_user.id}")  # Debug user info
    
    # For employees, return their own purchase orders
    if current_user.role == UserRole.EMPLOYEE:
        orders = db.query(PurchaseOrder).filter(PurchaseOrder.requested_by == current_user.id).all()
        print(f"Employee orders found: {len(orders)}")  # Debug count
        return orders
    
    # For reviewers (specialist, deputy MD, MD), show ones pending their approval
    if current_user.role == UserRole.SPECIALIST:
        orders = db.query(PurchaseOrder).filter(PurchaseOrder.status == PurchaseOrderStatus.PENDING).all()
        print(f"Specialist pending orders: {len(orders)}")  # Debug count
        return orders
    
    if current_user.role == UserRole.DEPUTY_MD:
        orders = db.query(PurchaseOrder).filter(
            PurchaseOrder.status == PurchaseOrderStatus.AWAITING_DEPUTY_MD,
            PurchaseOrder.cost <= 1000
        ).all()
        print(f"Deputy MD pending orders: {len(orders)}")  # Debug count
        return orders
    
    if current_user.role == UserRole.MD:
        orders = db.query(PurchaseOrder).all()
        # .filter(
        #     PurchaseOrder.status == PurchaseOrderStatus.AWAITING_MD,
        #     PurchaseOrder.cost > 1000
        # ).all()
        print(f"MD pending orders: {len(orders)}")  # Debug count
        return orders
    
    print(f"No matching role condition for: {current_user.role}")  # Debug role match
    return []


@router.get("/{id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed view of a purchase order including approval history"""
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order with id {id} not found"
        )
    
    # Check if user has permission to view this purchase order
    if current_user.role == UserRole.EMPLOYEE and purchase_order.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own purchase orders"
        )
    
    return purchase_order


@router.get("/{id}/approvals", response_model=List[ApprovalResponse])
async def get_purchase_order_approvals(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get chronological list of approval entries for a purchase order"""
    # First check if purchase order exists
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order with id {id} not found"
        )
    
    # Check if user has permission to view this purchase order's approvals
    if current_user.role == UserRole.EMPLOYEE and purchase_order.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view approvals for your own purchase orders"
        )
    
    # Get all approvals for this purchase order, ordered by approval date
    approvals = db.query(Approval).filter(
        Approval.purchase_order_id == id
    ).order_by(Approval.approved_at).all()
    
    return approvals


@router.post("/{id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    id: uuid.UUID,
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve or deny a purchase order (reviewers only)"""
    # Check if user is a reviewer
    if current_user.role not in [UserRole.SPECIALIST, UserRole.DEPUTY_MD, UserRole.MD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewers can approve purchase orders"
        )
    
    purchase_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == id).first()
    
    if not purchase_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order with id {id} not found"
        )
    
    # Check if the purchase order is in the correct state for this reviewer
    if current_user.role == UserRole.SPECIALIST and purchase_order.status != PurchaseOrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This purchase order is not pending specialist approval"
        )
    
    if current_user.role == UserRole.DEPUTY_MD and (
        purchase_order.status != PurchaseOrderStatus.AWAITING_DEPUTY_MD or purchase_order.cost > 1000
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This purchase order is not awaiting deputy MD approval or exceeds your approval limit"
        )
    
    if current_user.role == UserRole.MD and (
        purchase_order.status != PurchaseOrderStatus.AWAITING_MD or purchase_order.cost <= 1000
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This purchase order is not awaiting MD approval or is below your approval threshold"
        )
    
    # Create approval record
    new_approval = Approval(
        purchase_order_id=purchase_order.id,
        approved_by=current_user.id,
        role=current_user.role.value,
        status=approval.status,
        comments=approval.comments
    )
    
    db.add(new_approval)
    
    # Update purchase order status based on approval logic
    if approval.status == ApprovalStatus.DENIED:
        purchase_order.status = PurchaseOrderStatus.DENIED
    else:
        # Approval logic based on role
        if current_user.role == UserRole.SPECIALIST:
            # Route based on cost
            if purchase_order.cost > 1000:
                purchase_order.status = PurchaseOrderStatus.AWAITING_MD
            else:
                purchase_order.status = PurchaseOrderStatus.AWAITING_DEPUTY_MD
        elif current_user.role in [UserRole.DEPUTY_MD, UserRole.MD]:
            purchase_order.status = PurchaseOrderStatus.APPROVED
    
    db.commit()
    db.refresh(purchase_order)
    
    return purchase_order