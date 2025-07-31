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
    MANUFACTURED = "تم التصنيع"

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
    title: Optional[str] = None
    description: Optional[str] = None
    supervisor_name: Optional[str] = None  # اسم المشرف على التصنيع
    is_daily: bool = False  # هل هو أمر شغل يومي تلقائي
    work_date: Optional[str] = None  # تاريخ العمل للأوامر اليومية (stored as string)
    invoices: List[Dict[str, Any]] = Field(default_factory=list)  # الفواتير المرتبطة
    total_amount: float = 0.0
    total_items: int = 0
    status: str = "جديد"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # For backward compatibility
    invoice_id: Optional[str] = None
    items: List[Dict[str, Any]] = Field(default_factory=list)

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

# User management endpoints
@api_router.post("/users", response_model=User)
async def create_user(user: User):
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود بالفعل")
    
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return User(**user)

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": user.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return {"message": "تم تحديث المستخدم بنجاح"}

@api_router.delete("/users/clear-all")
async def clear_all_users():
    # Don't delete default users, only custom ones
    result = await db.users.delete_many({"username": {"$nin": ["Elsawy", "Root"]}})
    return {"message": f"تم حذف {result.deleted_count} مستخدم", "deleted_count": result.deleted_count}

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return {"message": "تم حذف المستخدم بنجاح"}

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

@api_router.delete("/customers/clear-all")
async def clear_all_customers():
    result = await db.customers.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} عميل", "deleted_count": result.deleted_count}

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="العميل غير موجود")
    return {"message": "تم حذف العميل بنجاح"}

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

@api_router.delete("/raw-materials/clear-all")
async def clear_all_raw_materials():
    result = await db.raw_materials.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} مادة خام", "deleted_count": result.deleted_count}

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

@api_router.delete("/finished-products/clear-all")
async def clear_all_finished_products():
    result = await db.finished_products.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} منتج جاهز", "deleted_count": result.deleted_count}

@api_router.delete("/finished-products/{product_id}")
async def delete_finished_product(product_id: str):
    result = await db.finished_products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    return {"message": "تم حذف المنتج بنجاح"}

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
async def create_invoice(invoice: InvoiceCreate, supervisor_name: str = ""):
    # Generate invoice number
    invoice_count = await db.invoices.count_documents({})
    invoice_number = f"INV-{invoice_count + 1:06d}"
    
    # Calculate totals
    total_amount = sum(item.total_price for item in invoice.items)
    remaining_amount = total_amount if invoice.payment_method == PaymentMethod.DEFERRED else 0
    status = InvoiceStatus.PENDING  # Always start with PENDING status
    
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
    
    # Add to daily work order automatically
    try:
        today = datetime.now().date()
        
        # Get or create daily work order for today
        daily_work_order = await db.work_orders.find_one({
            "is_daily": True,
            "work_date": today.isoformat()
        })
        
        if not daily_work_order:
            # Create new daily work order
            work_order = WorkOrder(
                title=f"أمر شغل يومي - {today.strftime('%d/%m/%Y')}",
                description=f"أمر شغل يومي لجميع فواتير يوم {today.strftime('%d/%m/%Y')}",
                supervisor_name=supervisor_name,
                is_daily=True,
                work_date=today,
                invoices=[],
                total_amount=0.0,
                total_items=0,
                status="جديد"
            )
            
            await db.work_orders.insert_one(work_order.dict())
            daily_work_order = work_order.dict()
        
        # Add invoice to daily work order
        invoice_for_work_order = invoice_obj.dict()
        if "_id" in invoice_for_work_order:
            del invoice_for_work_order["_id"]
            
        current_invoices = daily_work_order.get("invoices", [])
        current_invoices.append(invoice_for_work_order)
        
        new_total_amount = daily_work_order.get("total_amount", 0) + total_amount
        new_total_items = daily_work_order.get("total_items", 0) + len(invoice.items)
        
        await db.work_orders.update_one(
            {"id": daily_work_order["id"]},
            {"$set": {
                "invoices": current_invoices,
                "total_amount": new_total_amount,
                "total_items": new_total_items,
                "supervisor_name": supervisor_name  # Update supervisor name if provided
            }}
        )
        
    except Exception as e:
        # Log error but don't fail invoice creation
        print(f"Error adding invoice to daily work order: {str(e)}")
    
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

@api_router.delete("/invoices/clear-all")
async def clear_all_invoices():
    result = await db.invoices.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} فاتورة", "deleted_count": result.deleted_count}

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    result = await db.invoices.delete_one({"id": invoice_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
    return {"message": "تم حذف الفاتورة بنجاح"}

@api_router.put("/invoices/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, request: dict):
    try:
        # Extract status from request body
        if isinstance(request, dict) and 'status' in request:
            status = request['status']
        else:
            # Try parsing as direct string value
            status = request if isinstance(request, str) else str(request)
            
        result = await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": {"status": status}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        return {"message": "تم تحديث حالة الفاتورة", "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@api_router.delete("/payments/clear-all")
async def clear_all_payments():
    result = await db.payments.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} دفعة", "deleted_count": result.deleted_count}

@api_router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: str):
    result = await db.payments.delete_one({"id": payment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="الدفعة غير موجودة")
    return {"message": "تم حذف الدفعة بنجاح"}

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

@api_router.delete("/expenses/clear-all")
async def clear_all_expenses():
    result = await db.expenses.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} مصروف", "deleted_count": result.deleted_count}

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

@api_router.post("/work-orders/multiple")
async def create_work_order_multiple(work_order_data: dict):
    """Create work order from multiple invoices"""
    try:
        # Create work order with multiple invoices
        work_order = {
            "id": str(uuid.uuid4()),
            "title": work_order_data.get("title", ""),
            "description": work_order_data.get("description", ""),
            "priority": work_order_data.get("priority", "عادي"),
            "invoices": work_order_data.get("invoices", []),
            "total_amount": work_order_data.get("total_amount", 0),
            "total_items": work_order_data.get("total_items", 0),
            "status": "جديد",
            "created_at": datetime.utcnow()
        }
        
        await db.work_orders.insert_one(work_order)
        
        # Remove MongoDB ObjectId for return
        if "_id" in work_order:
            del work_order["_id"]
            
        return work_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/work-orders/daily/{work_date}")
async def get_or_create_daily_work_order(work_date: str, supervisor_name: str = ""):
    """Get or create daily work order for specified date"""
    try:
        # Parse date from string (YYYY-MM-DD format)
        work_date_obj = datetime.strptime(work_date, "%Y-%m-%d").date()
        
        # Check if daily work order already exists for this date
        existing_order = await db.work_orders.find_one({
            "is_daily": True,
            "work_date": work_date_obj.isoformat()  # Store as string
        })
        
        if existing_order:
            # Clean up MongoDB ObjectId
            if "_id" in existing_order:
                del existing_order["_id"]
            
            # Convert date to string for JSON serialization
            if "work_date" in existing_order and existing_order["work_date"]:
                existing_order["work_date"] = existing_order["work_date"] if isinstance(existing_order["work_date"], str) else existing_order["work_date"].isoformat()
                
            return existing_order
        
        # Create new daily work order
        work_order = WorkOrder(
            title=f"أمر شغل يومي - {work_date_obj.strftime('%d/%m/%Y')}",
            description=f"أمر شغل يومي لجميع فواتير يوم {work_date_obj.strftime('%d/%m/%Y')}",
            supervisor_name=supervisor_name,
            is_daily=True,
            work_date=work_date_obj,
            invoices=[],
            total_amount=0.0,
            total_items=0,
            status="جديد"
        )
        
        await db.work_orders.insert_one(work_order.dict())
        
        # Clean up MongoDB ObjectId for return
        work_order_dict = work_order.dict()
        if "_id" in work_order_dict:
            del work_order_dict["_id"]
        
        # Convert date to string for JSON serialization
        if "work_date" in work_order_dict and work_order_dict["work_date"]:
            work_order_dict["work_date"] = work_order_dict["work_date"].isoformat() if hasattr(work_order_dict["work_date"], 'isoformat') else str(work_order_dict["work_date"])
            
        return work_order_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/work-orders/daily/{work_order_id}/add-invoice")
async def add_invoice_to_daily_work_order(work_order_id: str, invoice_id: str):
    """Add invoice to daily work order"""
    try:
        # Get the work order
        work_order = await db.work_orders.find_one({"id": work_order_id})
        if not work_order:
            raise HTTPException(status_code=404, detail="أمر الشغل غير موجود")
        
        # Get the invoice
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        
        # Clean up MongoDB ObjectId from invoice
        if "_id" in invoice:
            del invoice["_id"]
        
        # Get current invoices
        current_invoices = work_order.get("invoices", [])
        
        # Check if invoice already exists
        if any(inv.get("id") == invoice_id for inv in current_invoices):
            return {"message": "الفاتورة موجودة بالفعل في أمر الشغل"}
            
        current_invoices.append(invoice)
        
        # Update totals
        new_total_amount = work_order.get("total_amount", 0) + invoice.get("total_amount", 0)
        new_total_items = work_order.get("total_items", 0) + len(invoice.get("items", []))
        
        # Update in database
        result = await db.work_orders.update_one(
            {"id": work_order_id},
            {"$set": {
                "invoices": current_invoices,
                "total_amount": new_total_amount,
                "total_items": new_total_items
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="فشل في تحديث أمر الشغل")
            
        return {"message": "تم إضافة الفاتورة إلى أمر الشغل اليومي بنجاح"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/work-orders")
async def get_work_orders():
    try:
        orders = await db.work_orders.find().sort("created_at", -1).to_list(1000)
        
        # Clean up MongoDB ObjectIds and handle date serialization
        for order in orders:
            if "_id" in order:
                del order["_id"]
            # Convert date to string for JSON serialization
            if "work_date" in order and order["work_date"]:
                order["work_date"] = order["work_date"] if isinstance(order["work_date"], str) else order["work_date"].isoformat()
                
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/work-orders/clear-all")
async def clear_all_work_orders():
    result = await db.work_orders.delete_many({})
    return {"message": f"تم حذف {result.deleted_count} أمر شغل", "deleted_count": result.deleted_count}

@api_router.delete("/work-orders/{work_order_id}")
async def delete_work_order(work_order_id: str):
    result = await db.work_orders.delete_one({"id": work_order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="أمر الشغل غير موجود")
    return {"message": "تم حذف أمر الشغل بنجاح"}

@api_router.put("/work-orders/{work_order_id}/add-invoice")
async def add_invoice_to_work_order(work_order_id: str, invoice_id: str):
    """Add an invoice to an existing work order"""
    try:
        # Get the work order
        work_order = await db.work_orders.find_one({"id": work_order_id})
        if not work_order:
            raise HTTPException(status_code=404, detail="أمر الشغل غير موجود")
            
        # Get the invoice
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
            
        # Clean invoice data
        if "_id" in invoice:
            del invoice["_id"]
            
        # Update work order with new invoice
        current_invoices = work_order.get("invoices", [])
        
        # Check if invoice already exists in work order
        if any(inv.get("id") == invoice_id for inv in current_invoices):
            raise HTTPException(status_code=400, detail="الفاتورة موجودة بالفعل في أمر الشغل")
            
        current_invoices.append(invoice)
        
        # Update totals
        new_total_amount = work_order.get("total_amount", 0) + invoice.get("total_amount", 0)
        new_total_items = work_order.get("total_items", 0) + len(invoice.get("items", []))
        
        # Update in database
        result = await db.work_orders.update_one(
            {"id": work_order_id},
            {"$set": {
                "invoices": current_invoices,
                "total_amount": new_total_amount,
                "total_items": new_total_items
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="فشل في تحديث أمر الشغل")
            
        return {"message": "تم إضافة الفاتورة إلى أمر الشغل بنجاح"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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