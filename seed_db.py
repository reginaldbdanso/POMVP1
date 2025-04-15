import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, PurchaseOrder, PurchaseOrderStatus
from app.auth.jwt import get_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    except SQLAlchemyError as e:
        logger.error(f"Error creating database session: {str(e)}")
        raise
    finally:
        db.close()

async def seed_database():
    try:
        # Create tables if they don't exist
        logger.info("Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        
        db = get_db()
        
        # Clear existing data
        logger.info("Clearing existing data...")
        try:
            db.query(PurchaseOrder).delete()
            db.query(User).delete()
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error clearing existing data: {str(e)}")
            raise
    
        logger.info("Creating users...")
        
        # Create 5 users with different roles
        users = [
        User(
            name="Employee User",
            username="employee",
            email="employee@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.EMPLOYEE,
            is_active=True
        ),
        User(
            name="Specialist User",
            username="specialist",
            email="specialist@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.SPECIALIST,
            is_active=True
        ),
        User(
            name="Manager User",
            username="manager",
            email="manager@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.MANAGER,
            is_active=True
        ),
        User(
            name="Deputy MD",
            username="deputy_md",
            email="deputy_md@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.DEPUTY_MD,
            is_active=True
        ),
        User(
            name="Managing Director",
            username="md",
            email="md@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.MD,
            is_active=True
        )
    ]
    
        # Add users to database
        try:
            for user in users:
                db.add(user)
            db.commit()
            
            # Refresh users to get their IDs
            for user in users:
                db.refresh(user)
            
            logger.info("Users created successfully!")
            
            # Create 3 purchase orders with varying amounts
            logger.info("Creating purchase orders...")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating users: {str(e)}")
            raise
    
        # Get the employee user for creating purchase orders
        employee = users[0]  # First user is the employee
        
        purchase_orders = [
            PurchaseOrder(
                item_name="Office Supplies",
                quantity=10,
                cost=500.00,  # Under 1000 threshold
                description="Various office supplies including pens, notebooks, and staplers",
                vendor_name="Office Depot",
                requested_by=employee.id,
                status=PurchaseOrderStatus.PENDING
            ),
            PurchaseOrder(
                item_name="Laptop Computer",
                quantity=1,
                cost=1500.00,  # Over 1000 threshold
                description="High-performance laptop for development work",
                vendor_name="Dell Technologies",
                requested_by=employee.id,
                status=PurchaseOrderStatus.PENDING
            ),
            PurchaseOrder(
                item_name="Office Furniture",
                quantity=5,
                cost=2500.00,  # Over 1000 threshold
                description="Ergonomic chairs and adjustable desks",
                vendor_name="IKEA Business",
                requested_by=employee.id,
                status=PurchaseOrderStatus.PENDING
            )
        ]
        
        # Add purchase orders to database
        try:
            for po in purchase_orders:
                db.add(po)
            db.commit()
            logger.info("Purchase orders created successfully!")
            logger.info("Database seeding completed!")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating purchase orders: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

# Run the seed function
if __name__ == "__main__":
    try:
        asyncio.run(seed_database())
    except Exception as e:
        logger.error(f"Failed to seed database: {str(e)}")
        raise