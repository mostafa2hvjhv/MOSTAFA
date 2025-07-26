from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class SealType(str, Enum):
    RSL = "RSL"
    RS = "RS"
    RSE = "RSE"
    B17 = "B17"
    B3 = "B3"
    B14 = "B14"
    B1 = "B1"
    R15 = "R15"
    R17 = "R17"
    W1 = "W1"
    W4 = "W4"
    W5 = "W5"
    W11 = "W11"
    WBT = "WBT"
    XR = "XR"
    CH = "CH"
    VR = "VR"

class MaterialType(str, Enum):
    NBR = "NBR"
    BUR = "BUR"
    BT = "BT"
    VT = "VT"
    BOOM = "BOOM"

class PaymentMethod(str, Enum):
    CASH = "نقدي"
    DEFERRED = "آجل"
    VODAFONE_SAWY = "فودافون كاش محمد الصاوي"
    VODAFONE_WAEL = "فودافون كاش وائل محمد"
    INSTAPAY = "انستاباي"

class ExpenseCategory(str, Enum):
    MATERIALS = "خامات"
    SALARIES = "رواتب"
    ELECTRICITY = "كهرباء"
    MAINTENANCE = "صيانة"
    OTHER = "أخرى"

class InvoiceStatus(str, Enum):
    PAID = "مدفوعة"
    UNPAID = "غير مدفوعة"
    PARTIAL = "مدفوعة جزئياً"
    PENDING = "انتظار"
    COMPLETED = "تم التنفيذ"

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RawMaterial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_type: MaterialType
    inner_diameter: float  # القطر الداخلي
    outer_diameter: float  # القطر الخارجي
    height: float  # الارتفاع بالملي
    pieces_count: int  # عدد القطع
    unit_code: str  # كود الوحدة
    cost_per_mm: float  # تكلفة الملي الواحد
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FinishedProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seal_type: SealType
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    height: float
    quantity: int
    unit_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvoiceItem(BaseModel):
    seal_type: SealType
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    height: float
    quantity: int
    unit_price: float
    total_price: float
    material_used: Optional[str] = None  # كود الوحدة للخامة المستخدمة

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    customer_id: str
    customer_name: str
    items: List[InvoiceItem]
    total_amount: float
    paid_amount: float = 0.0
    remaining_amount: float
    payment_method: PaymentMethod
    status: InvoiceStatus
    date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str
    amount: float
    payment_method: PaymentMethod
    date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    amount: float
    category: ExpenseCategory
    date: datetime = Field(default_factory=datetime.utcnow)

class WorkOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str
    items: List[Dict[str, Any]]  # Items with material codes
    status: str = "جديد"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request Models
class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class RawMaterialCreate(BaseModel):
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    height: float
    pieces_count: int
    unit_code: str
    cost_per_mm: float

class FinishedProductCreate(BaseModel):
    seal_type: SealType
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    height: float
    quantity: int
    unit_price: float

class InvoiceCreate(BaseModel):
    customer_id: Optional[str] = None
    customer_name: str
    items: List[InvoiceItem]
    payment_method: PaymentMethod
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_method: PaymentMethod
    notes: Optional[str] = None

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: ExpenseCategory

class CompatibilityCheck(BaseModel):
    seal_type: SealType
    inner_diameter: float
    outer_diameter: float
    height: float

# Auth endpoints
@api_router.post("/auth/login")
async def login(username: str, password: str):
    # Check predefined users
    predefined_users = {
        "Elsawy": {"password": "100100", "role": "admin"},
        "Root": {"password": "master", "role": "user"}
    }
    
    if username in predefined_users and predefined_users[username]["password"] == password:
        return {
            "success": True,
            "user": {
                "username": username,
                "role": predefined_users[username]["role"]
            }
        }
    
    # Check database users
    user = await db.users.find_one({"username": username, "password": password})
    if user:
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"]
            }
        }
    
    raise HTTPException(status_code=401, detail="خطأ في اسم المستخدم أو كلمة المرور")

# Dashboard endpoints
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    # Get totals from database
    invoices = list(await db.invoices.find().to_list(1000))
    expenses = list(await db.expenses.find().to_list(1000))
    customers = list(await db.customers.find().to_list(1000))
    
    total_sales = sum(invoice.get("total_amount", 0) for invoice in invoices)
    total_expenses = sum(expense.get("amount", 0) for expense in expenses)
    total_unpaid = sum(invoice.get("remaining_amount", 0) for invoice in invoices if invoice.get("remaining_amount", 0) > 0)
    
    return {
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "net_profit": total_sales - total_expenses,
        "total_unpaid": total_unpaid,
        "invoice_count": len(invoices),
        "customer_count": len(customers)
    }

# Customer endpoints
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_dict = customer.dict()
    customer_obj = Customer(**customer_dict)
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="العميل غير موجود")
    return Customer(**customer)

# Raw materials endpoints
@api_router.post("/raw-materials", response_model=RawMaterial)
async def create_raw_material(material: RawMaterialCreate):
    material_dict = material.dict()
    material_obj = RawMaterial(**material_dict)
    await db.raw_materials.insert_one(material_obj.dict())
    return material_obj

@api_router.get("/raw-materials", response_model=List[RawMaterial])
async def get_raw_materials():
    materials = await db.raw_materials.find().to_list(1000)
    return [RawMaterial(**material) for material in materials]

@api_router.put("/raw-materials/{material_id}")
async def update_raw_material(material_id: str, material: RawMaterialCreate):
    result = await db.raw_materials.update_one(
        {"id": material_id},
        {"$set": material.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="المادة غير موجودة")
    return {"message": "تم تحديث المادة بنجاح"}

@api_router.delete("/raw-materials/{material_id}")
async def delete_raw_material(material_id: str):
    result = await db.raw_materials.delete_one({"id": material_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المادة غير موجودة")
    return {"message": "تم حذف المادة بنجاح"}

# Finished products endpoints
@api_router.post("/finished-products", response_model=FinishedProduct)
async def create_finished_product(product: FinishedProductCreate):
    product_dict = product.dict()
    product_obj = FinishedProduct(**product_dict)
    await db.finished_products.insert_one(product_obj.dict())
    return product_obj

@api_router.get("/finished-products", response_model=List[FinishedProduct])
async def get_finished_products():
    products = await db.finished_products.find().to_list(1000)
    return [FinishedProduct(**product) for product in products]

# Compatibility check endpoint
@api_router.post("/compatibility-check")
async def check_compatibility(check: CompatibilityCheck):
    # Get raw materials
    raw_materials = await db.raw_materials.find().to_list(1000)
    finished_products = await db.finished_products.find().to_list(1000)
    
    compatible_materials = []
    compatible_products = []
    
    # Check raw materials
    for material in raw_materials:
        # Remove MongoDB ObjectId if present
        if "_id" in material:
            del material["_id"]
            
        # Material compatibility logic:
        # - Inner diameter of material <= seal inner diameter
        # - Outer diameter of material >= seal outer diameter  
        # - Height of material >= seal height + 5mm
        if (material["inner_diameter"] <= check.inner_diameter and 
            material["outer_diameter"] >= check.outer_diameter and
            material["height"] >= (check.height + 5)):
            
            warning = ""
            if material["height"] < (check.height + 5):
                warning = "تحذير: الارتفاع غير كافي"
            
            compatible_materials.append({
                **material,
                "warning": warning,
                "low_stock": material["height"] < 20
            })
    
    # Check finished products
    for product in finished_products:
        # Remove MongoDB ObjectId if present
        if "_id" in product:
            del product["_id"]
            
        if (product["seal_type"] == check.seal_type and
            product["inner_diameter"] == check.inner_diameter and
            product["outer_diameter"] == check.outer_diameter and
            product["height"] == check.height):
            compatible_products.append(product)
    
    return {
        "compatible_materials": compatible_materials,
        "compatible_products": compatible_products
    }

# Invoice endpoints
@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate):
    # Generate invoice number
    invoice_count = await db.invoices.count_documents({})
    invoice_number = f"INV-{invoice_count + 1:06d}"
    
    # Calculate totals
    total_amount = sum(item.total_price for item in invoice.items)
    remaining_amount = total_amount if invoice.payment_method == PaymentMethod.DEFERRED else 0
    status = InvoiceStatus.UNPAID if invoice.payment_method == PaymentMethod.DEFERRED else InvoiceStatus.PAID
    
    invoice_dict = invoice.dict()
    invoice_obj = Invoice(
        invoice_number=invoice_number,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        status=status,
        **invoice_dict
    )
    
    # Update inventory
    for item in invoice.items:
        if item.material_used:
            # Deduct from raw materials (height - (seal_height + 2mm))
            await db.raw_materials.update_one(
                {"unit_code": item.material_used},
                {"$inc": {"height": -(item.height + 2) * item.quantity}}
            )
    
    await db.invoices.insert_one(invoice_obj.dict())
    return invoice_obj

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    invoices = await db.invoices.find().sort("date", -1).to_list(1000)
    return [Invoice(**invoice) for invoice in invoices]

@api_router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    return Invoice(**invoice)

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    result = await db.invoices.delete_one({"id": invoice_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    return {"message": "تم حذف الفاتورة بنجاح"}

@api_router.put("/invoices/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, status: InvoiceStatus):
    result = await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    return {"message": "تم تحديث حالة الفاتورة"}

# Payment endpoints
@api_router.post("/payments", response_model=Payment)
async def create_payment(payment: PaymentCreate):
    payment_obj = Payment(**payment.dict())
    
    # Update invoice
    invoice = await db.invoices.find_one({"id": payment.invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    
    new_paid_amount = invoice["paid_amount"] + payment.amount
    new_remaining = invoice["total_amount"] - new_paid_amount
    
    status = InvoiceStatus.PAID if new_remaining <= 0 else InvoiceStatus.PARTIAL
    
    await db.invoices.update_one(
        {"id": payment.invoice_id},
        {"$set": {
            "paid_amount": new_paid_amount,
            "remaining_amount": max(0, new_remaining),
            "status": status
        }}
    )
    
    await db.payments.insert_one(payment_obj.dict())
    return payment_obj

@api_router.get("/payments", response_model=List[Payment])
async def get_payments():
    payments = await db.payments.find().sort("date", -1).to_list(1000)
    return [Payment(**payment) for payment in payments]

# Expense endpoints
@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    expense_obj = Expense(**expense.dict())
    await db.expenses.insert_one(expense_obj.dict())
    return expense_obj

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses():
    expenses = await db.expenses.find().sort("date", -1).to_list(1000)
    return [Expense(**expense) for expense in expenses]

@api_router.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: str):
    result = await db.expenses.delete_one({"id": expense_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المصروف غير موجود")
    return {"message": "تم حذف المصروف بنجاح"}

# Revenue reports
@api_router.get("/reports/revenue")
async def get_revenue_report(period: str = "daily"):
    # Implementation for revenue reports based on period
    invoices = list(await db.invoices.find().to_list(1000))
    expenses = list(await db.expenses.find().to_list(1000))
    
    total_revenue = sum(invoice.get("total_amount", 0) for invoice in invoices)
    total_expenses = sum(expense.get("amount", 0) for expense in expenses)
    material_cost = sum(expense.get("amount", 0) for expense in expenses if expense.get("category") == "خامات")
    
    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "material_cost": material_cost,
        "profit": total_revenue - total_expenses,
        "period": period
    }

# Work orders
@api_router.post("/work-orders", response_model=WorkOrder)
async def create_work_order(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    
    work_order = WorkOrder(
        invoice_id=invoice_id,
        items=invoice["items"]
    )
    
    await db.work_orders.insert_one(work_order.dict())
    return work_order

@api_router.get("/work-orders", response_model=List[WorkOrder])
async def get_work_orders():
    orders = await db.work_orders.find().sort("created_at", -1).to_list(1000)
    return [WorkOrder(**order) for order in orders]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()