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
    YAD_ELSAWY = "يد الصاوي"

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
    permissions: Optional[List[str]] = Field(default_factory=list)
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
    # Fields for manufactured products
    seal_type: Optional[SealType] = None
    material_type: Optional[MaterialType] = None
    inner_diameter: Optional[float] = None
    outer_diameter: Optional[float] = None
    height: Optional[float] = None
    # Common fields
    quantity: int
    unit_price: float
    total_price: float
    # Product type
    product_type: Optional[str] = "manufactured"  # "manufactured" or "local"
    # Fields for local products
    product_name: Optional[str] = None
    supplier: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    local_product_details: Optional[Dict[str, Any]] = None
    # Fields for manufactured products
    material_used: Optional[str] = None  # كود الوحدة للخامة المستخدمة
    material_details: Optional[Dict[str, Any]] = None  # تفاصيل الخامة المختارة

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    customer_id: Optional[str] = None
    customer_name: str
    invoice_title: Optional[str] = None  # عنوان الفاتورة
    supervisor_name: Optional[str] = None  # اسم المشرف
    items: List[InvoiceItem]
    subtotal: Optional[float] = None  # المجموع الفرعي قبل الخصم
    discount: Optional[float] = 0.0  # مبلغ الخصم
    discount_type: Optional[str] = "amount"  # نوع الخصم: amount أو percentage
    discount_value: Optional[float] = 0.0  # القيمة المدخلة للخصم
    total_after_discount: Optional[float] = None  # الإجمالي بعد الخصم
    total_amount: float  # الإجمالي النهائي (same as total_after_discount for compatibility)
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
    invoice_title: Optional[str] = None  # عنوان الفاتورة
    supervisor_name: Optional[str] = None  # اسم المشرف
    items: List[InvoiceItem]
    payment_method: PaymentMethod
    discount_type: Optional[str] = "amount"  # نوع الخصم: amount أو percentage
    discount_value: Optional[float] = 0.0  # القيمة المدخلة للخصم
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_method: PaymentMethod
    notes: Optional[str] = None

class TreasuryTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str  # نوع الحساب (cash, vodafone_elsawy, etc.)
    transaction_type: str  # income, expense, transfer_in, transfer_out
    amount: float
    description: str
    reference: Optional[str] = None
    related_transaction_id: Optional[str] = None  # للتحويلات
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Supplier and Local Product Models
class Supplier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    total_purchases: Optional[float] = 0.0  # إجمالي المشتريات
    total_paid: Optional[float] = 0.0  # إجمالي المدفوع
    balance: Optional[float] = 0.0  # الرصيد المستحق
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LocalProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    supplier_id: str
    supplier_name: str
    purchase_price: float
    selling_price: float
    current_stock: Optional[int] = 0
    total_purchased: Optional[int] = 0
    total_sold: Optional[int] = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SupplierTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str
    supplier_name: str
    transaction_type: str  # "purchase" or "payment"
    amount: float
    description: str
    product_name: Optional[str] = None  # للمشتريات
    quantity: Optional[int] = None  # للمشتريات
    unit_price: Optional[float] = None  # للمشتريات
    payment_method: Optional[str] = None  # للدفعات
    reference_invoice_id: Optional[str] = None  # مرجع الفاتورة إذا كان من بيع منتج محلي
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Inventory Management Models
class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    available_height: float  # الارتفاع المتاح في الجرد
    min_stock_level: Optional[float] = 10.0  # الحد الأدنى للمخزون
    max_stock_level: Optional[float] = 1000.0  # الحد الأقصى للمخزون
    unit_code: str  # كود مميز للعنصر
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class InventoryTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    inventory_item_id: str
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    transaction_type: str  # "in" (إضافة) أو "out" (استهلاك)
    height_change: float  # التغيير في الارتفاع (موجب للإضافة، سالب للاستهلاك)
    remaining_height: float  # الارتفاع المتبقي بعد المعاملة
    reason: str  # سبب المعاملة
    reference_id: Optional[str] = None  # مرجع المعاملة (فاتورة، طلب خام، إلخ)
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TreasuryTransactionCreate(BaseModel):
    account_id: str
    transaction_type: str
    amount: float
    description: str
    reference: Optional[str] = None

class SupplierCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class LocalProductCreate(BaseModel):
    name: str
    supplier_id: str
    purchase_price: float
    selling_price: float
    current_stock: Optional[int] = 0

class SupplierTransactionCreate(BaseModel):
    supplier_id: str
    transaction_type: str
    amount: float
    description: str
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    payment_method: Optional[str] = None

class InventoryItemCreate(BaseModel):
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    available_height: float
    min_stock_level: Optional[float] = 10.0
    max_stock_level: Optional[float] = 1000.0
    unit_code: str
    notes: Optional[str] = None

class InventoryTransactionCreate(BaseModel):
    inventory_item_id: Optional[str] = None  # يمكن أن يكون فارغ للإضافة التلقائية
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    transaction_type: str
    height_change: float
    reason: str
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    related_transaction_id: Optional[str] = None

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
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
    """Create raw material with inventory check"""
    try:
        # Check inventory availability
        inventory_check = await check_inventory_availability(
            material_type=material.material_type,
            inner_diameter=material.inner_diameter,
            outer_diameter=material.outer_diameter,
            required_height=material.height * material.pieces_count
        )
        
        if not inventory_check["available"]:
            raise HTTPException(
                status_code=400, 
                detail=f"لا يمكن إضافة المادة الخام. {inventory_check['message']}. المطلوب: {material.height * material.pieces_count} مم، المتاح: {inventory_check['available_height']} مم"
            )
        
        # Create raw material
        material_dict = material.dict()
        material_obj = RawMaterial(**material_dict)
        await db.raw_materials.insert_one(material_obj.dict())
        
        # Deduct from inventory
        deduction_amount = material.height * material.pieces_count
        inventory_transaction = InventoryTransactionCreate(
            inventory_item_id=inventory_check["inventory_item_id"],
            material_type=material.material_type,
            inner_diameter=material.inner_diameter,
            outer_diameter=material.outer_diameter,
            transaction_type="out",
            height_change=-deduction_amount,
            reason=f"إضافة مادة خام جديدة: {material.unit_code}",
            reference_id=material_obj.id,
            notes=f"خصم {deduction_amount} مم لإنتاج {material.pieces_count} قطعة بارتفاع {material.height} مم لكل قطعة"
        )
        
        # Create inventory transaction
        await create_inventory_transaction(inventory_transaction)
        
        return material_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
    # Calculate totals with discount
    subtotal = sum(item.total_price for item in invoice.items)
    
    # Handle discount calculation
    discount_amount = 0.0
    if hasattr(invoice, 'discount') and invoice.discount is not None:
        discount_amount = invoice.discount
    elif hasattr(invoice, 'discount_value') and invoice.discount_value is not None:
        # Calculate discount based on type
        if hasattr(invoice, 'discount_type') and invoice.discount_type == 'percentage':
            discount_amount = (subtotal * invoice.discount_value) / 100
        else:
            discount_amount = invoice.discount_value
    
    total_after_discount = subtotal - discount_amount
    remaining_amount = total_after_discount if invoice.payment_method == PaymentMethod.DEFERRED else 0
    status = InvoiceStatus.PENDING  # Always start with PENDING status
    
    invoice_dict = invoice.dict()
    invoice_obj = Invoice(
        invoice_number=invoice_number,
        subtotal=subtotal,
        discount=discount_amount,
        total_after_discount=total_after_discount,
        total_amount=total_after_discount,  # للتوافق مع الكود الموجود
        remaining_amount=remaining_amount,
        status=status,
        **invoice_dict
    )
    
    # Update inventory and handle local products
    for item in invoice.items:
        if hasattr(item, 'product_type') and item.product_type == 'local':
            # Handle local product sale
            if hasattr(item, 'local_product_details') and item.local_product_details:
                # Update local product stock
                await db.local_products.update_one(
                    {"name": item.local_product_details.get("name"), 
                     "supplier": item.local_product_details.get("supplier")},
                    {"$inc": {"total_sold": item.quantity}}
                )
                
                # Create supplier transaction for purchase cost
                supplier_transaction = SupplierTransaction(
                    supplier_id="", # We'll need to find this based on supplier name
                    supplier_name=item.local_product_details.get("supplier", ""),
                    transaction_type="purchase",
                    amount=item.local_product_details.get("purchase_price", 0) * item.quantity,
                    description=f"شراء {item.local_product_details.get('name')} من فاتورة {invoice_number}",
                    product_name=item.local_product_details.get("name", ""),
                    quantity=item.quantity,
                    unit_price=item.local_product_details.get("purchase_price", 0),
                    reference_invoice_id=invoice_obj.id
                )
                
                # Find supplier by name to get ID
                supplier = await db.suppliers.find_one({"name": item.local_product_details.get("supplier", "")})
                if supplier:
                    supplier_transaction.supplier_id = supplier["id"]
                    await db.supplier_transactions.insert_one(supplier_transaction.dict())
                    
                    # Update supplier balance
                    purchase_amount = item.local_product_details.get("purchase_price", 0) * item.quantity
                    await db.suppliers.update_one(
                        {"id": supplier["id"]},
                        {
                            "$inc": {
                                "total_purchases": purchase_amount,
                                "balance": purchase_amount
                            }
                        }
                    )
        else:
            # Handle manufactured products (existing logic)
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
                work_date=today.isoformat(),  # Store as string
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
        
        new_total_amount = daily_work_order.get("total_amount", 0) + total_after_discount
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
            work_date=work_date_obj.isoformat(),  # Store as string
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

# Treasury Management APIs
@api_router.get("/treasury/transactions")
async def get_treasury_transactions():
    """Get all treasury transactions"""
    try:
        transactions = await db.treasury_transactions.find().sort("date", -1).to_list(1000)
        
        # Clean up MongoDB ObjectIds
        for transaction in transactions:
            if "_id" in transaction:
                del transaction["_id"]
                
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/treasury/transactions")
async def create_treasury_transaction(transaction: TreasuryTransactionCreate):
    """Create a new treasury transaction"""
    try:
        transaction_obj = TreasuryTransaction(**transaction.dict())
        await db.treasury_transactions.insert_one(transaction_obj.dict())
        
        transaction_dict = transaction_obj.dict()
        if "_id" in transaction_dict:
            del transaction_dict["_id"]
            
        return transaction_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/treasury/transfer")
async def transfer_funds(transfer: TransferRequest):
    """Transfer funds between accounts"""
    try:
        # Create outgoing transaction
        out_transaction = TreasuryTransaction(
            account_id=transfer.from_account,
            transaction_type="transfer_out",
            amount=transfer.amount,
            description=f"تحويل إلى حساب {transfer.to_account}",
            reference=transfer.notes or "تحويل داخلي"
        )
        
        # Create incoming transaction
        in_transaction = TreasuryTransaction(
            account_id=transfer.to_account,
            transaction_type="transfer_in",
            amount=transfer.amount,
            description=f"تحويل من حساب {transfer.from_account}",
            reference=transfer.notes or "تحويل داخلي",
            related_transaction_id=out_transaction.id
        )
        
        # Link transactions
        out_transaction.related_transaction_id = in_transaction.id
        
        # Save both transactions
        await db.treasury_transactions.insert_one(out_transaction.dict())
        await db.treasury_transactions.insert_one(in_transaction.dict())
        
        return {"message": "تم التحويل بنجاح", "transfer_id": out_transaction.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/treasury/balances")
async def get_account_balances():
    """Get current balances for all accounts"""
    try:
        # Get all transactions
        transactions = await db.treasury_transactions.find().to_list(10000)
        
        # Get invoice data for automatic transactions
        invoices = await db.invoices.find().to_list(1000)
        expenses = await db.expenses.find().to_list(1000)
        
        # Calculate balances
        account_balances = {
            'cash': 0,
            'vodafone_elsawy': 0,
            'vodafone_wael': 0,
            'deferred': 0,
            'instapay': 0,
            'yad_elsawy': 0
        }
        
        # Add invoice amounts
        payment_method_map = {
            'نقدي': 'cash',
            'فودافون كاش محمد الصاوي': 'vodafone_elsawy',
            'فودافون كاش وائل محمد': 'vodafone_wael',
            'آجل': 'deferred',
            'انستاباي': 'instapay',
            'يد الصاوي': 'yad_elsawy'
        }
        
        for invoice in invoices:
            account_id = payment_method_map.get(invoice.get('payment_method'))
            if account_id:
                account_balances[account_id] += invoice.get('total_amount', 0)
        
        # Subtract expenses from cash
        for expense in expenses:
            account_balances['cash'] -= expense.get('amount', 0)
        
        # Apply manual transactions
        for transaction in transactions:
            account_id = transaction.get('account_id')
            if account_id in account_balances:
                amount = transaction.get('amount', 0)
                transaction_type = transaction.get('transaction_type')
                
                if transaction_type in ['income', 'transfer_in']:
                    account_balances[account_id] += amount
                elif transaction_type in ['expense', 'transfer_out']:
                    account_balances[account_id] -= amount
        
        return account_balances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suppliers endpoints
@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = await db.suppliers.find({}).to_list(None)
        return suppliers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/suppliers", response_model=Supplier)
async def create_supplier(supplier: SupplierCreate):
    """Create a new supplier"""
    try:
        supplier_obj = Supplier(**supplier.dict())
        await db.suppliers.insert_one(supplier_obj.dict())
        
        supplier_dict = supplier_obj.dict()
        if "_id" in supplier_dict:
            del supplier_dict["_id"]
        return supplier_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/suppliers/{supplier_id}")
async def update_supplier(supplier_id: str, supplier: SupplierCreate):
    """Update supplier information"""
    try:
        result = await db.suppliers.update_one(
            {"id": supplier_id},
            {"$set": supplier.dict()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        return {"message": "تم تحديث بيانات المورد بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: str):
    """Delete a supplier"""
    try:
        result = await db.suppliers.delete_one({"id": supplier_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        return {"message": "تم حذف المورد بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Local Products endpoints
@api_router.get("/local-products", response_model=List[LocalProduct])
async def get_local_products():
    """Get all local products"""
    try:
        products = await db.local_products.find({}).to_list(None)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/local-products/supplier/{supplier_id}", response_model=List[LocalProduct])
async def get_products_by_supplier(supplier_id: str):
    """Get products by supplier"""
    try:
        products = await db.local_products.find({"supplier_id": supplier_id}).to_list(None)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/local-products", response_model=LocalProduct)
async def create_local_product(product: LocalProductCreate):
    """Create a new local product"""
    try:
        # Get supplier name
        supplier = await db.suppliers.find_one({"id": product.supplier_id})
        if not supplier:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        
        product_obj = LocalProduct(
            **product.dict(),
            supplier_name=supplier["name"]
        )
        await db.local_products.insert_one(product_obj.dict())
        
        product_dict = product_obj.dict()
        if "_id" in product_dict:
            del product_dict["_id"]
        return product_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/local-products/{product_id}")
async def update_local_product(product_id: str, product: LocalProductCreate):
    """Update local product"""
    try:
        # Get supplier name
        supplier = await db.suppliers.find_one({"id": product.supplier_id})
        if not supplier:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        
        update_data = product.dict()
        update_data["supplier_name"] = supplier["name"]
        
        result = await db.local_products.update_one(
            {"id": product_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="المنتج غير موجود")
        return {"message": "تم تحديث المنتج بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/local-products/{product_id}")
async def delete_local_product(product_id: str):
    """Delete a local product"""
    try:
        result = await db.local_products.delete_one({"id": product_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="المنتج غير موجود")
        return {"message": "تم حذف المنتج بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Supplier Transactions endpoints
@api_router.get("/supplier-transactions", response_model=List[SupplierTransaction])
async def get_supplier_transactions():
    """Get all supplier transactions"""
    try:
        transactions = await db.supplier_transactions.find({}).sort("date", -1).to_list(None)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/supplier-transactions/{supplier_id}", response_model=List[SupplierTransaction])
async def get_supplier_transactions_by_id(supplier_id: str):
    """Get transactions for a specific supplier"""
    try:
        transactions = await db.supplier_transactions.find({"supplier_id": supplier_id}).sort("date", -1).to_list(None)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/supplier-transactions", response_model=SupplierTransaction)
async def create_supplier_transaction(transaction: SupplierTransactionCreate):
    """Create a supplier transaction (purchase or payment)"""
    try:
        # Get supplier name
        supplier = await db.suppliers.find_one({"id": transaction.supplier_id})
        if not supplier:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        
        transaction_obj = SupplierTransaction(
            **transaction.dict(),
            supplier_name=supplier["name"]
        )
        await db.supplier_transactions.insert_one(transaction_obj.dict())
        
        # Update supplier balance
        if transaction.transaction_type == "purchase":
            # Increase supplier balance (we owe them)
            await db.suppliers.update_one(
                {"id": transaction.supplier_id},
                {
                    "$inc": {
                        "total_purchases": transaction.amount,
                        "balance": transaction.amount
                    }
                }
            )
        elif transaction.transaction_type == "payment":
            # Decrease supplier balance (we paid them)
            await db.suppliers.update_one(
                {"id": transaction.supplier_id},
                {
                    "$inc": {
                        "total_paid": transaction.amount,
                        "balance": -transaction.amount
                    }
                }
            )
        
        transaction_dict = transaction_obj.dict()
        if "_id" in transaction_dict:
            del transaction_dict["_id"]
        return transaction_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/supplier-payment")
async def pay_supplier(supplier_id: str, amount: float, payment_method: str = "cash"):
    """Pay a supplier and deduct from treasury"""
    try:
        # Get supplier
        supplier = await db.suppliers.find_one({"id": supplier_id})
        if not supplier:
            raise HTTPException(status_code=404, detail="المورد غير موجود")
        
        # Create supplier payment transaction
        supplier_transaction = SupplierTransaction(
            supplier_id=supplier_id,
            supplier_name=supplier["name"],
            transaction_type="payment",
            amount=amount,
            description=f"دفع للمورد {supplier['name']}",
            payment_method=payment_method
        )
        await db.supplier_transactions.insert_one(supplier_transaction.dict())
        
        # Update supplier balance
        await db.suppliers.update_one(
            {"id": supplier_id},
            {
                "$inc": {
                    "total_paid": amount,
                    "balance": -amount
                }
            }
        )
        
        # Create treasury transaction (expense)
        treasury_transaction = TreasuryTransaction(
            account_id=payment_method,
            transaction_type="expense",
            amount=amount,
            description=f"دفع للمورد {supplier['name']}",
            reference=f"supplier_payment_{supplier_transaction.id}"
        )
        await db.treasury_transactions.insert_one(treasury_transaction.dict())
        
        return {"message": "تم دفع المبلغ للمورد بنجاح", "payment_id": supplier_transaction.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inventory Management endpoints
@api_router.get("/inventory", response_model=List[InventoryItem])
async def get_inventory():
    """Get all inventory items"""
    try:
        items = await db.inventory.find({}).to_list(None)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory/low-stock")
async def get_low_stock_items():
    """Get items with stock below minimum level"""
    try:
        pipeline = [
            {
                "$match": {
                    "$expr": {
                        "$lt": ["$available_height", "$min_stock_level"]
                    }
                }
            }
        ]
        items = await db.inventory.aggregate(pipeline).to_list(None)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: str):
    """Get specific inventory item"""
    try:
        item = await db.inventory.find_one({"id": item_id})
        if not item:
            raise HTTPException(status_code=404, detail="العنصر غير موجود في الجرد")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inventory", response_model=InventoryItem)
async def create_inventory_item(item: InventoryItemCreate):
    """Create a new inventory item"""
    try:
        # Check if item with same specifications already exists
        existing_item = await db.inventory.find_one({
            "material_type": item.material_type,
            "inner_diameter": item.inner_diameter,
            "outer_diameter": item.outer_diameter
        })
        
        if existing_item:
            raise HTTPException(
                status_code=400, 
                detail=f"عنصر بنفس المواصفات موجود بالفعل: {existing_item['unit_code']}"
            )
        
        inventory_item = InventoryItem(**item.dict())
        await db.inventory.insert_one(inventory_item.dict())
        
        # Create initial transaction
        initial_transaction = InventoryTransaction(
            inventory_item_id=inventory_item.id,
            material_type=item.material_type,
            inner_diameter=item.inner_diameter,
            outer_diameter=item.outer_diameter,
            transaction_type="in",
            height_change=item.available_height,
            remaining_height=item.available_height,
            reason="إضافة عنصر جديد للجرد",
            reference_id=inventory_item.id,
            notes=f"إنشاء عنصر جديد: {item.unit_code}"
        )
        await db.inventory_transactions.insert_one(initial_transaction.dict())
        
        item_dict = inventory_item.dict()
        if "_id" in item_dict:
            del item_dict["_id"]
        return item_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/inventory/{item_id}")
async def update_inventory_item(item_id: str, item: InventoryItemCreate):
    """Update inventory item"""
    try:
        result = await db.inventory.update_one(
            {"id": item_id},
            {
                "$set": {
                    **item.dict(),
                    "last_updated": datetime.utcnow()
                }
            }
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="العنصر غير موجود في الجرد")
        return {"message": "تم تحديث عنصر الجرد بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    """Delete inventory item"""
    try:
        result = await db.inventory.delete_one({"id": item_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="العنصر غير موجود في الجرد")
        return {"message": "تم حذف عنصر الجرد بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory-transactions", response_model=List[InventoryTransaction])
async def get_inventory_transactions():
    """Get all inventory transactions"""
    try:
        transactions = await db.inventory_transactions.find({}).sort("date", -1).to_list(None)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory-transactions/{item_id}", response_model=List[InventoryTransaction])
async def get_inventory_transactions_by_item(item_id: str):
    """Get transactions for a specific inventory item"""
    try:
        transactions = await db.inventory_transactions.find(
            {"inventory_item_id": item_id}
        ).sort("date", -1).to_list(None)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inventory-transactions", response_model=InventoryTransaction)
async def create_inventory_transaction(transaction: InventoryTransactionCreate):
    """Create inventory transaction (in/out)"""
    try:
        # Find inventory item by specifications if item_id not provided
        if not transaction.inventory_item_id:
            inventory_item = await db.inventory.find_one({
                "material_type": transaction.material_type,
                "inner_diameter": transaction.inner_diameter,
                "outer_diameter": transaction.outer_diameter
            })
            
            if not inventory_item:
                raise HTTPException(
                    status_code=404, 
                    detail=f"لا يوجد عنصر في الجرد بالمواصفات المطلوبة: {transaction.material_type} - {transaction.inner_diameter}x{transaction.outer_diameter}"
                )
            transaction.inventory_item_id = inventory_item["id"]
        else:
            inventory_item = await db.inventory.find_one({"id": transaction.inventory_item_id})
            if not inventory_item:
                raise HTTPException(status_code=404, detail="العنصر غير موجود في الجرد")
        
        # Check if there's enough stock for "out" transactions
        if transaction.transaction_type == "out" and abs(transaction.height_change) > inventory_item["available_height"]:
            raise HTTPException(
                status_code=400, 
                detail=f"المخزون غير كافي. المتاح: {inventory_item['available_height']}، المطلوب: {abs(transaction.height_change)}"
            )
        
        # Calculate new remaining height
        new_height = inventory_item["available_height"] + transaction.height_change
        if new_height < 0:
            new_height = 0
        
        # Create transaction
        transaction_obj = InventoryTransaction(
            **transaction.dict(),
            remaining_height=new_height
        )
        await db.inventory_transactions.insert_one(transaction_obj.dict())
        
        # Update inventory item
        await db.inventory.update_one(
            {"id": transaction.inventory_item_id},
            {
                "$set": {
                    "available_height": new_height,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        transaction_dict = transaction_obj.dict()
        if "_id" in transaction_dict:
            del transaction_dict["_id"]
        return transaction_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inventory/check-availability")
async def check_inventory_availability(
    material_type: MaterialType, 
    inner_diameter: float, 
    outer_diameter: float, 
    required_height: float
):
    """Check if material is available in inventory with required height"""
    try:
        inventory_item = await db.inventory.find_one({
            "material_type": material_type,
            "inner_diameter": inner_diameter,
            "outer_diameter": outer_diameter
        })
        
        if not inventory_item:
            return {
                "available": False,
                "message": f"المادة الخام غير متوفرة في الجرد: {material_type} - {inner_diameter}x{outer_diameter}",
                "available_height": 0,
                "required_height": required_height
            }
        
        available_height = inventory_item.get("available_height", 0)
        is_available = available_height >= required_height
        
        return {
            "available": is_available,
            "message": f"{'المادة متوفرة' if is_available else 'المادة غير متوفرة بالكمية المطلوبة'}",
            "available_height": available_height,
            "required_height": required_height,
            "inventory_item_id": inventory_item["id"],
            "unit_code": inventory_item.get("unit_code", "")
        }
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