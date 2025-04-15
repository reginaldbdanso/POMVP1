from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, auth, purchase_orders

app = FastAPI(
    title="Purchase Order Management System",
    description="API for managing purchase orders and approvals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])

@app.get("/")
async def root():
    return {"message": "Welcome to Purchase Order Management System API"}