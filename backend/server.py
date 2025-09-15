from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import pandas as pd
import io

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

class MaterialPricing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_type: MaterialType
    inner_diameter: float  # القطر الداخلي
    outer_diameter: float  # القطر الخارجي
    price_per_mm: float  # سعر الملي الواحد
    manufacturing_cost_client1: float  # تكلفة التصنيع - عميل 1
    manufacturing_cost_client2: float  # تكلفة التصنيع - عميل 2  
    manufacturing_cost_client3: float  # تكلفة التصنيع - عميل 3
    notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Pricing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_type: str
    material_type: str
    price_per_unit: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    selected_materials: Optional[List[Dict[str, Any]]] = None  # الخامات المتعددة المختارة
    notes: Optional[str] = None  # ملاحظات على المنتج

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
    
    class Config:
        use_enum_values = True

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str
    amount: float
    payment_method: PaymentMethod
    date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True

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
    unit_code: Optional[str] = None  # سيتم توليده تلقائياً
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
    
    class Config:
        use_enum_values = True

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    payment_method: PaymentMethod
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True

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
    available_pieces: int  # تغيير من available_height إلى available_pieces
    min_stock_level: Optional[int] = 2  # الحد الأدنى 2 قطعة
    # إزالة max_stock_level و unit_code
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
    pieces_change: int  # التغيير في عدد القطع (موجب للإضافة، سالب للاستهلاك)
    remaining_pieces: int  # عدد القطع المتبقية بعد المعاملة
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
    available_pieces: int  # تغيير من available_height إلى available_pieces
    min_stock_level: Optional[int] = 2  # الحد الأدنى 2 قطعة
    notes: Optional[str] = None

class InventoryTransactionCreate(BaseModel):
    inventory_item_id: Optional[str] = None  # يمكن أن يكون فارغ للإضافة التلقائية
    material_type: MaterialType
    inner_diameter: float
    outer_diameter: float
    transaction_type: str
    pieces_change: int  # التغيير في عدد القطع
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
    material_type: Optional[MaterialType] = None

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
# Material code generation helper
async def generate_unit_code(material_type: str, inner_diameter: float, outer_diameter: float):
    """Generate automatic unit code based on material type and specifications"""
    # Material type to prefix mapping
    type_prefix = {
        "BUR": "B",
        "NBR": "N", 
        "BT": "T",
        "VT": "V",
        "BOOM": "M"
    }
    
    prefix = type_prefix.get(material_type, "X")  # Default to X if type not found
    
    # Find existing materials with same specifications
    existing_materials = await db.raw_materials.find({
        "material_type": material_type,
        "inner_diameter": inner_diameter,
        "outer_diameter": outer_diameter
    }).to_list(None)
    
    # Get the highest sequence number
    max_sequence = 0
    for mat in existing_materials:
        unit_code = mat.get("unit_code", "")
        if unit_code.startswith(f"{prefix}-"):
            try:
                sequence = int(unit_code.split("-")[1])
                max_sequence = max(max_sequence, sequence)
            except (IndexError, ValueError):
                continue
    
    # Generate new code with next sequence number
    new_sequence = max_sequence + 1
    return f"{prefix}-{new_sequence}"

@api_router.post("/raw-materials", response_model=RawMaterial)
async def create_raw_material(material: RawMaterialCreate):
    """Create raw material with inventory check and automatic unit code"""
    try:
        # Generate automatic unit code
        auto_unit_code = await generate_unit_code(
            material.material_type,
            material.inner_diameter, 
            material.outer_diameter
        )
        
        # Check inventory availability
        inventory_check = await check_inventory_availability(
            material_type=material.material_type,
            inner_diameter=material.inner_diameter,
            outer_diameter=material.outer_diameter,
            required_pieces=material.pieces_count
        )
        
        if not inventory_check["available"]:
            raise HTTPException(
                status_code=400, 
                detail=f"لا يمكن إضافة المادة الخام. {inventory_check['message']}. المطلوب: {material.pieces_count} قطعة، المتاح: {inventory_check['available_pieces']} قطعة"
            )
        
        # Create raw material with auto-generated unit code
        material_dict = material.dict()
        material_dict["unit_code"] = auto_unit_code  # Override with auto-generated code
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
            pieces_change=-material.pieces_count,
            reason=f"إضافة مادة خام جديدة: {auto_unit_code}",
            reference_id=material_obj.id,
            notes=f"خصم {material.pieces_count} قطعة لإنتاج {material.pieces_count} قطعة بارتفاع {material.height} مم لكل قطعة"
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
    """Get all raw materials sorted by material type priority then size"""
    # Define material type priority order: BUR-NBR-BT-BOOM-VT
    material_priority = {'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5}
    
    # Get all materials first
    materials = await db.raw_materials.find().to_list(1000)
    
    # Sort by material type priority, then by diameter
    sorted_materials = sorted(materials, key=lambda x: (
        material_priority.get(x.get('material_type', ''), 6),  # Material priority
        x.get('inner_diameter', 0),  # Then inner diameter
        x.get('outer_diameter', 0)   # Then outer diameter
    ))
    
    return [RawMaterial(**material) for material in sorted_materials]

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

@api_router.put("/finished-products/{product_id}")
async def update_finished_product(product_id: str, product_update: FinishedProductCreate):
    updated_data = product_update.dict()
    
    # Check if product exists
    existing_product = await db.finished_products.find_one({"id": product_id})
    if not existing_product:
        raise HTTPException(status_code=404, detail="المنتج غير موجود")
    
    # Update the product
    result = await db.finished_products.update_one(
        {"id": product_id},
        {"$set": updated_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="لم يتم تحديث أي بيانات")
    
    # Get updated product
    updated_product = await db.finished_products.find_one({"id": product_id})
    if "_id" in updated_product:
        del updated_product["_id"]
    
    return updated_product

# Compatibility check endpoint
@api_router.post("/compatibility-check")
async def check_compatibility(check: CompatibilityCheck):
    # Get raw materials
    raw_materials = await db.raw_materials.find().to_list(1000)
    finished_products = await db.finished_products.find().to_list(1000)
    
    compatible_materials = []
    compatible_products = []
    
    # Define tolerance ranges for better compatibility matching
    # Especially important for converted measurements from inches
    tolerance_percentage = 0.1  # 10% tolerance
    
    inner_tolerance = check.inner_diameter * tolerance_percentage
    outer_tolerance = check.outer_diameter * tolerance_percentage
    height_tolerance = max(5.0, check.height * tolerance_percentage)  # Minimum 5mm or 10%
    
    # Check raw materials
    for material in raw_materials:
        # Remove MongoDB ObjectId if present
        if "_id" in material:
            del material["_id"]
            
        # Material type filter - if specified, only show materials of that type
        if check.material_type and material.get("material_type") != check.material_type:
            continue
            
        # CRITICAL: Filter materials based on usability after consumption
        # Don't show materials if using them would leave < 15mm (unusable waste)
        if material.get("height", 0) <= 15:
            continue
            
        # Calculate required material height for one seal
        required_height_per_seal = check.height + 2
        
        # Check if material can produce at least 1 seal AND remain >= 15mm or become 0
        material_height = material.get("height", 0)
        remaining_after_one_seal = material_height - required_height_per_seal
        
        # Skip material if it would leave unusable waste (1-14mm range)
        if remaining_after_one_seal > 0 and remaining_after_one_seal < 15:
            continue
        
        inner_compatible = material["inner_diameter"] <= (check.inner_diameter + inner_tolerance)
        outer_compatible = material["outer_diameter"] >= (check.outer_diameter - outer_tolerance)
        height_compatible = material_height >= required_height_per_seal
        
        if inner_compatible and outer_compatible and height_compatible:
            
            warning = ""
            compatibility_score = 100
            
            # Calculate compatibility warnings and scoring
            if material["height"] < (check.height + 5):
                warning = "تحذير: الارتفاع قريب من الحد الأدنى"
                compatibility_score -= 10
            
            if material["inner_diameter"] > check.inner_diameter:
                warning += " - القطر الداخلي أكبر قليلاً"
                compatibility_score -= 5
                
            if material["outer_diameter"] < check.outer_diameter:
                warning += " - القطر الخارجي أصغر قليلاً" 
                compatibility_score -= 5
            
            # Add exact match bonus
            if (abs(material["inner_diameter"] - check.inner_diameter) < 1 and
                abs(material["outer_diameter"] - check.outer_diameter) < 1):
                compatibility_score += 10
                if not warning:
                    warning = "مطابقة ممتازة"
            
            compatible_materials.append({
                **material,
                "warning": warning.strip(" -"),
                "compatibility_score": compatibility_score,
                "low_stock": material.get("height", 0) < 20,
                "tolerance_used": {
                    "inner_tolerance": inner_tolerance,
                    "outer_tolerance": outer_tolerance,
                    "height_tolerance": height_tolerance
                }
            })
    
    # Sort by compatibility score (highest first)
    compatible_materials.sort(key=lambda x: x.get("compatibility_score", 0), reverse=True)
    
    # Check finished products (keep exact matching for finished products)
    for product in finished_products:
        # Remove MongoDB ObjectId if present
        if "_id" in product:
            del product["_id"]
            
        # Check seal type and material compatibility with small tolerance
        inner_match = abs(product["inner_diameter"] - check.inner_diameter) <= 1
        outer_match = abs(product["outer_diameter"] - check.outer_diameter) <= 1
        height_match = abs(product["height"] - check.height) <= 1
        
        if (product["seal_type"] == check.seal_type and
            inner_match and outer_match and height_match):
            compatible_products.append(product)
    
    return {
        "compatible_materials": compatible_materials,
        "compatible_products": compatible_products,
        "search_criteria": {
            "inner_diameter": check.inner_diameter,
            "outer_diameter": check.outer_diameter, 
            "height": check.height,
            "tolerances_applied": {
                "inner_tolerance": inner_tolerance,
                "outer_tolerance": outer_tolerance,
                "height_tolerance": height_tolerance
            }
        }
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
    remaining_amount = total_after_discount if str(invoice.payment_method) == "آجل" else 0
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
            # Handle manufactured products - deduct from material height
            material_deducted = False  # Flag to prevent double deduction
            
            # Prioritize multi-material selection over single material selection
            if hasattr(item, 'selected_materials') and item.selected_materials and not material_deducted:
                # Handle multiple materials with specified seal counts
                for material_info in item.selected_materials:
                    raw_material = await db.raw_materials.find_one({
                        "unit_code": material_info.get("unit_code"),
                        "inner_diameter": material_info.get("inner_diameter"),
                        "outer_diameter": material_info.get("outer_diameter")
                    })
                    
                    if raw_material:
                        seal_consumption_per_piece = item.height + 2
                        seals_to_produce = material_info.get("seals_count", 0)
                        material_consumption = seals_to_produce * seal_consumption_per_piece
                        current_height = raw_material.get("height", 0)
                        
                        if current_height >= material_consumption:
                            # Deduct from this material
                            await db.raw_materials.update_one(
                                {"id": raw_material["id"]},
                                {"$inc": {"height": -material_consumption}}
                            )
                            
                            remaining_height = current_height - material_consumption
                            print(f"✅ تم خصم {material_consumption} مم من الخامة {raw_material.get('unit_code', 'غير محدد')} لإنتاج {seals_to_produce} سيل - المتبقي: {remaining_height} مم")
                        else:
                            print(f"❌ خطأ: لا يوجد ارتفاع كافٍ في الخامة {raw_material.get('unit_code', 'غير محدد')} - مطلوب: {material_consumption} مم، متوفر: {current_height} مم")
                    else:
                        print(f"❌ خطأ: لم يتم العثور على الخامة {material_info.get('unit_code', 'غير محدد')}")
                
                material_deducted = True
                print(f"🎉 تم خصم المواد من {len(item.selected_materials)} خامة مختلفة")
                
            # Prioritize material_details (single material) if no multi-material selection
            elif item.material_details and not material_deducted:
                material_details = item.material_details
                if not material_details.get('is_finished_product', False):
                    # Find the specific material selected by user
                    raw_material = None
                    
                    # Search by inner_diameter + outer_diameter + unit_code together for highest accuracy
                    if (material_details.get("inner_diameter") and 
                        material_details.get("outer_diameter") and 
                        material_details.get("unit_code")):
                        raw_material = await db.raw_materials.find_one({
                            "inner_diameter": material_details.get("inner_diameter"),
                            "outer_diameter": material_details.get("outer_diameter"),
                            "unit_code": material_details.get("unit_code")
                        })
                    
                    # If not found by dimensions + unit_code, try by specifications only
                    if not raw_material and material_details.get("material_type"):
                        raw_material = await db.raw_materials.find_one({
                            "material_type": material_details.get("material_type"),
                            "inner_diameter": material_details.get("inner_diameter"),
                            "outer_diameter": material_details.get("outer_diameter")
                        })
                    
                    if raw_material:
                        # Calculate actual seals to be made from this material
                        seal_consumption_per_piece = item.height + 2
                        total_seals_requested = item.quantity
                        material_height = raw_material.get("height", 0)
                        
                        # Calculate maximum seals possible from this material
                        max_possible_seals = int(material_height // seal_consumption_per_piece)
                        
                        # Check if remaining height would be unusable (< 15mm but > 0)
                        remaining_after_max = material_height - (max_possible_seals * seal_consumption_per_piece)
                        if remaining_after_max > 0 and remaining_after_max < 15 and max_possible_seals > 0:
                            max_possible_seals -= 1  # Reduce by 1 to avoid unusable remainder
                        
                        # Determine actual seals to produce (limited by material availability)
                        actual_seals_to_produce = min(total_seals_requested, max_possible_seals)
                        material_consumption = actual_seals_to_produce * seal_consumption_per_piece
                        
                        if actual_seals_to_produce > 0 and material_height >= material_consumption:
                            # Deduct from material height
                            await db.raw_materials.update_one(
                                {"id": raw_material["id"]},
                                {"$inc": {"height": -material_consumption}}
                            )
                            
                            material_deducted = True
                            remaining_height = material_height - material_consumption
                            
                            if actual_seals_to_produce < total_seals_requested:
                                print(f"⚠️ تم خصم {material_consumption} مم من الخامة {raw_material.get('unit_code', 'غير محدد')} لإنتاج {actual_seals_to_produce} سيل من أصل {total_seals_requested} سيل - المتبقي: {remaining_height} مم")
                                print(f"📌 ملاحظة: يحتاج المستخدم لاختيار خامة أخرى لإنتاج الـ {total_seals_requested - actual_seals_to_produce} سيل المتبقية")
                            else:
                                print(f"✅ تم خصم {material_consumption} مم من الخامة {raw_material.get('unit_code', 'غير محدد')} لإنتاج جميع الـ {total_seals_requested} سيل - المتبقي: {remaining_height} مم")
                        else:
                            if max_possible_seals <= 0:
                                print(f"❌ خطأ: الخامة {raw_material.get('unit_code', 'غير محدد')} لا تكفي لإنتاج أي سيل - الارتفاع: {material_height} مم، المطلوب: {seal_consumption_per_piece} مم للسيل الواحد")
                            else:
                                print(f"❌ خطأ: لا يوجد ارتفاع كافٍ في الخامة {raw_material.get('unit_code', 'غير محدد')} - مطلوب: {material_consumption} مم، متوفر: {material_height} مم")
                    else:
                        print(f"❌ خطأ: لم يتم العثور على الخامة المحددة - {material_details.get('material_type')} {material_details.get('inner_diameter')}×{material_details.get('outer_diameter')} كود: {material_details.get('unit_code', 'غير محدد')}")
            
            # Fallback to material_used only if material_details didn't work and no deduction happened
            if item.material_used and not material_deducted:
                # Find the raw material by unit_code only (less accurate fallback)
                raw_material = await db.raw_materials.find_one({"unit_code": item.material_used})
                
                if raw_material:
                    # Calculate required material consumption (seal height + 2mm waste) * quantity
                    material_consumption = (item.height + 2) * item.quantity
                    
                    # Check if there's enough height available
                    current_height = raw_material.get("height", 0)
                    if current_height >= material_consumption:
                        # Deduct from material height
                        await db.raw_materials.update_one(
                            {"unit_code": item.material_used},
                            {"$inc": {"height": -material_consumption}}
                        )
                        
                        material_deducted = True
                        print(f"⚠️ تم خصم {material_consumption} مم من ارتفاع الخامة {item.material_used} (بحث بكود الوحدة فقط - أقل دقة)")
                    else:
                        print(f"❌ تحذير: لا يوجد ارتفاع كافٍ في الخامة {item.material_used} - مطلوب: {material_consumption} مم، متوفر: {current_height} مم")
                else:
                    print(f"❌ تحذير: الخامة {item.material_used} غير موجودة في المواد الخام")
    
    await db.invoices.insert_one(invoice_obj.dict())
    
    # Add treasury transaction for non-deferred payments
    if str(invoice.payment_method) != "آجل":  # التحقق من النص العربي
        # Map payment methods to treasury account IDs
        payment_method_mapping = {
            "نقدي": "cash",
            "آجل": "deferred",
            "فودافون كاش محمد الصاوي": "vodafone_elsawy", 
            "فودافون كاش وائل محمد": "vodafone_wael",
            "انستاباي": "instapay",
            "يد الصاوي": "yad_elsawy"
        }
        
        account_id = payment_method_mapping.get(str(invoice.payment_method), "cash")
        
        # Check if treasury transaction already exists for this invoice
        existing_transaction = await db.treasury_transactions.find_one({
            "reference": f"invoice_{invoice_obj.id}"
        })
        
        if not existing_transaction:
            treasury_transaction = TreasuryTransaction(
                account_id=account_id,
                transaction_type="income",
                amount=total_after_discount,
                description=f"فاتورة {invoice_number} - {invoice.customer_name}",
                reference=f"invoice_{invoice_obj.id}"
            )
            await db.treasury_transactions.insert_one(treasury_transaction.dict())
    
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
        
        # Add invoice to daily work order with enhanced material details
        invoice_for_work_order = invoice_obj.dict()
        if "_id" in invoice_for_work_order:
            del invoice_for_work_order["_id"]
        
        # Enhance items with material usage details for work order display
        enhanced_items = []
        for item in invoice_for_work_order.get("items", []):
            enhanced_item = item.copy()
            
            # Add material consumption details for manufactured products
            if item.get("product_type") == "manufactured":
                seal_consumption = (item.get("height", 0) + 2) * item.get("quantity", 0)
                
                # Build material info string based on selected materials
                material_info = ""
                unit_code_display = ""
                
                print(f"🔍 Debug - Item data: {item}")
                print(f"🔍 Debug - Selected materials: {item.get('selected_materials')}")
                
                if item.get("selected_materials"):
                    print(f"✅ Found selected_materials: {len(item.get('selected_materials'))} materials")
                    # Multi-material case
                    material_parts = []
                    for mat in item.get("selected_materials", []):
                        inner_dia = mat.get("inner_diameter", 0)
                        outer_dia = mat.get("outer_diameter", 0) 
                        unit_code = mat.get("unit_code", "غير محدد")
                        seals_count = mat.get("seals_count", 0)
                        material_parts.append(f"{inner_dia}×{outer_dia} {unit_code} ({seals_count})")
                    
                    unit_code_display = " / ".join(material_parts)
                    material_info = f"مواد متعددة: {len(item.get('selected_materials', []))} خامة"
                    print(f"✅ Multi-material unit_code_display: {unit_code_display}")
                    
                elif item.get("material_details"):
                    # Single material case
                    mat_details = item.get("material_details")
                    inner_dia = mat_details.get("inner_diameter", 0)
                    outer_dia = mat_details.get("outer_diameter", 0)
                    unit_code = mat_details.get("unit_code", "غير محدد")
                    unit_code_display = f"{inner_dia}×{outer_dia} {unit_code} ({item.get('quantity', 0)})"
                    material_info = f"{unit_code} ({item.get('quantity', 0)} سيل)"
                    
                elif item.get("material_used"):
                    # Fallback case
                    unit_code_display = f"{item.get('material_used')} ({item.get('quantity', 0)})"
                    material_info = f"{item.get('material_used')} ({item.get('quantity', 0)} سيل)"
                
                enhanced_item["material_consumption"] = seal_consumption
                enhanced_item["material_info"] = material_info
                enhanced_item["unit_code_display"] = unit_code_display  # This will be used in work order
                enhanced_item["work_order_display"] = f"{item.get('seal_type', '')} {item.get('material_type', '')} {item.get('inner_diameter', 0)}×{item.get('outer_diameter', 0)}×{item.get('height', 0)} - {material_info} - استهلاك: {seal_consumption} مم"
            
            enhanced_items.append(enhanced_item)
        
        invoice_for_work_order["items"] = enhanced_items
            
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

@api_router.put("/invoices/{invoice_id}")
async def update_invoice(invoice_id: str, invoice_update: dict):
    """Update invoice details"""
    try:
        # Find existing invoice
        existing_invoice = await db.invoices.find_one({"id": invoice_id})
        if not existing_invoice:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        
        # Handle items update and calculate subtotal
        if 'items' in invoice_update:
            subtotal = sum(item.get('total_price', 0) for item in invoice_update['items'])
            invoice_update['subtotal'] = subtotal
        else:
            # Get current subtotal from existing invoice
            subtotal = existing_invoice.get('subtotal', 0)
            
        # Handle discount calculation (independent of items update)
        discount_amount = 0.0
        if 'discount_type' in invoice_update and 'discount_value' in invoice_update:
            discount_value = float(invoice_update.get('discount_value', 0))
            if invoice_update['discount_type'] == 'percentage':
                discount_amount = (subtotal * discount_value) / 100
            else:
                discount_amount = discount_value
            
            # Update discount and totals
            total_after_discount = subtotal - discount_amount
            invoice_update.update({
                'discount': discount_amount,
                'total_after_discount': total_after_discount,
                'total_amount': total_after_discount
            })
        elif 'discount' in invoice_update:
            discount_amount = float(invoice_update.get('discount', 0))
            total_after_discount = subtotal - discount_amount
            invoice_update.update({
                'total_after_discount': total_after_discount,
                'total_amount': total_after_discount
            })
        
        # Update the invoice
        result = await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": invoice_update}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        
        return {"message": "تم تحديث الفاتورة بنجاح"}
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
    
    # Add treasury transaction for the payment
    payment_method_mapping = {
        "نقدي": "cash",
        "آجل": "deferred",
        "فودافون كاش محمد الصاوي": "vodafone_elsawy", 
        "فودافون كاش وائل محمد": "vodafone_wael",
        "انستاباي": "instapay",
        "يد الصاوي": "yad_elsawy"
    }
    
    payment_method_str = str(payment.payment_method)
    account_id = payment_method_mapping.get(payment_method_str, "cash")
    
    # Check if treasury transaction already exists for this payment
    existing_transaction = await db.treasury_transactions.find_one({
        "reference": f"payment_{payment_obj.id}"
    })
    
    if not existing_transaction:
        # Add income transaction to the payment account
        treasury_transaction = TreasuryTransaction(
            account_id=account_id,
            transaction_type="income",
            amount=payment.amount,
            description=f"دفع فاتورة {invoice['invoice_number']} - {invoice['customer_name']}",
            reference=f"payment_{payment_obj.id}"
        )
        await db.treasury_transactions.insert_one(treasury_transaction.dict())
        
        # For deferred invoices, also create a deduction from deferred account
        if invoice.get("payment_method") == "آجل":
            deferred_transaction = TreasuryTransaction(
                account_id="deferred",
                transaction_type="expense",
                amount=payment.amount,
                description=f"تسديد آجل فاتورة {invoice['invoice_number']} - {invoice['customer_name']}",
                reference=f"payment_{payment_obj.id}_deferred"
            )
            await db.treasury_transactions.insert_one(deferred_transaction.dict())
    
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
        
        # Add invoice amounts (only for deferred invoices that don't have treasury transactions)
        payment_method_map = {
            'نقدي': 'cash',
            'فودافون كاش محمد الصاوي': 'vodafone_elsawy',
            'فودافون كاش وائل محمد': 'vodafone_wael',
            'آجل': 'deferred',
            'انستاباي': 'instapay',
            'يد الصاوي': 'yad_elsawy'
        }
        
        # Only add deferred invoices directly (non-deferred invoices are handled by treasury transactions)
        for invoice in invoices:
            if invoice.get('payment_method') == 'آجل':
                account_balances['deferred'] += invoice.get('total_amount', 0)
        
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
    """Get all inventory items sorted by material type priority then size"""
    try:
        # Define material type priority order: BUR-NBR-BT-BOOM-VT
        material_priority = {'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5}
        
        # Get all items first
        items = await db.inventory_items.find({}).to_list(None)
        
        # Sort by material type priority, then by diameter
        sorted_items = sorted(items, key=lambda x: (
            material_priority.get(x.get('material_type', ''), 6),  # Material priority
            x.get('inner_diameter', 0),  # Then inner diameter
            x.get('outer_diameter', 0)   # Then outer diameter
        ))
        
        return sorted_items
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
                        "$lt": ["$available_pieces", "$min_stock_level"]
                    }
                }
            }
        ]
        items = await db.inventory_items.aggregate(pipeline).to_list(None)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: str):
    """Get specific inventory item"""
    try:
        item = await db.inventory_items.find_one({"id": item_id})
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
        existing_item = await db.inventory_items.find_one({
            "material_type": item.material_type,
            "inner_diameter": item.inner_diameter,
            "outer_diameter": item.outer_diameter
        })
        
        if existing_item:
            raise HTTPException(
                status_code=400, 
                detail=f"عنصر بنفس المواصفات موجود بالفعل: {item.material_type} - {item.inner_diameter}x{item.outer_diameter}"
            )
        
        inventory_item = InventoryItem(**item.dict())
        await db.inventory_items.insert_one(inventory_item.dict())
        
        # Create initial transaction
        initial_transaction = InventoryTransaction(
            inventory_item_id=inventory_item.id,
            material_type=item.material_type,
            inner_diameter=item.inner_diameter,
            outer_diameter=item.outer_diameter,
            transaction_type="in",
            pieces_change=item.available_pieces,
            remaining_pieces=item.available_pieces,
            reason="إضافة عنصر جديد للجرد",
            reference_id=inventory_item.id,
            notes=f"إنشاء عنصر جديد: {item.material_type} - {item.inner_diameter}x{item.outer_diameter}"
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
        result = await db.inventory_items.update_one(
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
        result = await db.inventory_items.delete_one({"id": item_id})
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
        
        # Clean transactions for response - handle old schema compatibility
        cleaned_transactions = []
        for transaction in transactions:
            # Handle old schema fields (height_change -> pieces_change, remaining_height -> remaining_pieces)
            if "height_change" in transaction and "pieces_change" not in transaction:
                transaction["pieces_change"] = transaction.get("height_change", 0)
            if "remaining_height" in transaction and "remaining_pieces" not in transaction:
                transaction["remaining_pieces"] = transaction.get("remaining_height", 0)
            
            # Ensure required fields exist
            if "pieces_change" not in transaction:
                transaction["pieces_change"] = 0
            if "remaining_pieces" not in transaction:
                transaction["remaining_pieces"] = 0
                
            cleaned_transactions.append(transaction)
            
        return cleaned_transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory-transactions/{item_id}", response_model=List[InventoryTransaction])
async def get_inventory_transactions_by_item(item_id: str):
    """Get transactions for a specific inventory item"""
    try:
        transactions = await db.inventory_transactions.find(
            {"inventory_item_id": item_id}
        ).sort("date", -1).to_list(None)
        
        # Clean transactions for response - handle old schema compatibility
        cleaned_transactions = []
        for transaction in transactions:
            # Handle old schema fields
            if "height_change" in transaction and "pieces_change" not in transaction:
                transaction["pieces_change"] = transaction.get("height_change", 0)
            if "remaining_height" in transaction and "remaining_pieces" not in transaction:
                transaction["remaining_pieces"] = transaction.get("remaining_height", 0)
            
            # Ensure required fields exist
            if "pieces_change" not in transaction:
                transaction["pieces_change"] = 0
            if "remaining_pieces" not in transaction:
                transaction["remaining_pieces"] = 0
                
            cleaned_transactions.append(transaction)
            
        return cleaned_transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Material Pricing APIs
@api_router.get("/material-pricing", response_model=List[MaterialPricing])
async def get_material_pricing():
    """Get all material pricing"""
    try:
        pricings = await db.material_pricing.find({}).sort("created_at", -1).to_list(None)
        return [MaterialPricing(**pricing) for pricing in pricings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/material-pricing", response_model=MaterialPricing)
async def create_material_pricing(pricing: MaterialPricing):
    """Create new material pricing"""
    try:
        pricing_dict = pricing.dict()
        await db.material_pricing.insert_one(pricing_dict)
        return pricing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/material-pricing/{pricing_id}")
async def update_material_pricing(pricing_id: str, pricing: MaterialPricing):
    """Update material pricing"""
    try:
        pricing_dict = pricing.dict()
        pricing_dict["updated_at"] = datetime.utcnow()
        
        result = await db.material_pricing.update_one(
            {"id": pricing_id},
            {"$set": pricing_dict}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="التسعيرة غير موجودة")
        return {"message": "تم تحديث التسعيرة بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/material-pricing/{pricing_id}")
async def delete_material_pricing(pricing_id: str):
    """Delete material pricing"""
    try:
        result = await db.material_pricing.delete_one({"id": pricing_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="التسعيرة غير موجودة")
        return {"message": "تم حذف التسعيرة بنجاح"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/calculate-price")
async def calculate_material_price(
    material_type: str,
    inner_diameter: float,
    outer_diameter: float,
    height: float,
    client_type: int  # 1, 2, or 3
):
    """Calculate price based on material pricing"""
    try:
        # Find matching material pricing
        pricing = await db.material_pricing.find_one({
            "material_type": material_type,
            "inner_diameter": inner_diameter,
            "outer_diameter": outer_diameter
        })
        
        if not pricing:
            raise HTTPException(status_code=404, detail="لم يتم العثور على تسعيرة مطابقة لهذه الخامة")
        
        # Calculate price: (price_per_mm * height) + manufacturing_cost
        mm_cost = pricing["price_per_mm"] * height
        
        if client_type == 1:
            manufacturing_cost = pricing["manufacturing_cost_client1"]
        elif client_type == 2:
            manufacturing_cost = pricing["manufacturing_cost_client2"]
        elif client_type == 3:
            manufacturing_cost = pricing["manufacturing_cost_client3"]
        else:
            raise HTTPException(status_code=400, detail="نوع العميل يجب أن يكون 1، 2، أو 3")
        
        total_price = mm_cost + manufacturing_cost
        
        return {
            "material_type": material_type,
            "dimensions": f"{inner_diameter}×{outer_diameter}×{height}",
            "price_per_mm": pricing["price_per_mm"],
            "mm_cost": mm_cost,
            "manufacturing_cost": manufacturing_cost,
            "client_type": client_type,
            "total_price": total_price,
            "pricing_id": pricing["id"]
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Treasury Reset API (Only for Elsawy)
@api_router.post("/treasury/reset")
async def reset_treasury(username: str):
    """Reset all treasury data - Only for Elsawy user"""
    try:
        # Security check - only Elsawy can perform this operation
        if username != "Elsawy":
            raise HTTPException(status_code=403, detail="غير مصرح لك بتنفيذ هذه العملية")
        
        # Get count of records before deletion for logging
        treasury_count = await db.treasury_transactions.count_documents({})
        
        # Delete all treasury transactions
        treasury_result = await db.treasury_transactions.delete_many({})
        
        return {
            "message": "تم مسح جميع بيانات الخزينة بنجاح",
            "deleted_treasury_transactions": treasury_result.deleted_count,
            "reset_by": username,
            "reset_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Change Invoice Payment Method API
@api_router.put("/invoices/{invoice_id}/change-payment-method")
async def change_invoice_payment_method(
    invoice_id: str, 
    new_payment_method: str,
    username: str = None
):
    """Change invoice payment method and update treasury transactions"""
    try:
        # Find the invoice
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        
        old_payment_method = invoice.get("payment_method")
        if old_payment_method == new_payment_method:
            return {"message": "طريقة الدفع هي نفسها بالفعل"}
        
        # Map payment methods to treasury account IDs
        payment_method_mapping = {
            "نقدي": "cash",
            "آجل": "deferred",
            "فودافون كاش محمد الصاوي": "vodafone_elsawy", 
            "فودافون كاش وائل محمد": "vodafone_wael",
            "انستاباي": "instapay",
            "يد الصاوي": "yad_elsawy"
        }
        
        old_account_id = payment_method_mapping.get(old_payment_method)
        new_account_id = payment_method_mapping.get(new_payment_method)
        
        # Special handling for deferred payment method
        if old_payment_method == "آجل":
            old_account_id = "deferred"  # Special case for deferred
        if new_payment_method == "آجل":
            new_account_id = "deferred"  # Special case for deferred
        
        if not old_account_id or not new_account_id:
            raise HTTPException(status_code=400, detail="طريقة الدفع غير مدعومة")
        
        invoice_amount = invoice.get("total_amount", 0)
        transfer_reference = f"تحويل دفع فاتورة {invoice.get('invoice_number')} من {old_payment_method} إلى {new_payment_method}"
        
        # Handle treasury transactions based on payment method types
        transactions_created = []
        
        # Case 1: Converting FROM deferred TO immediate payment method
        if old_payment_method == "آجل" and new_payment_method != "آجل":
            # Create income transaction for the new payment method
            new_transaction = TreasuryTransaction(
                account_id=new_account_id,
                transaction_type="income",
                amount=invoice_amount,
                description=f"تحويل من آجل إلى {new_payment_method} - {transfer_reference}",
                reference=f"تحويل-{invoice.get('invoice_number')}"
            )
            await db.treasury_transactions.insert_one(new_transaction.dict())
            transactions_created.append("income")
            
        # Case 2: Converting FROM immediate payment method TO deferred
        elif old_payment_method != "آجل" and new_payment_method == "آجل":
            # Create expense transaction to remove from old payment method
            old_transaction = TreasuryTransaction(
                account_id=old_account_id,
                transaction_type="expense",
                amount=invoice_amount,
                description=f"تحويل من {old_payment_method} إلى آجل - {transfer_reference}",
                reference=f"تحويل-{invoice.get('invoice_number')}"
            )
            await db.treasury_transactions.insert_one(old_transaction.dict())
            transactions_created.append("expense")
            
        # Case 3: Converting between immediate payment methods (not deferred)
        elif old_payment_method != "آجل" and new_payment_method != "آجل":
            # Remove from old account
            old_transaction = TreasuryTransaction(
                account_id=old_account_id,
                transaction_type="expense",
                amount=invoice_amount,
                description=f"خصم لتحويل طريقة الدفع - {transfer_reference}",
                reference=f"تحويل-{invoice.get('invoice_number')}"
            )
            await db.treasury_transactions.insert_one(old_transaction.dict())
            
            # Add to new account
            new_transaction = TreasuryTransaction(
                account_id=new_account_id,
                transaction_type="income",
                amount=invoice_amount,
                description=f"إضافة من تحويل طريقة الدفع - {transfer_reference}",
                reference=f"تحويل-{invoice.get('invoice_number')}"
            )
            await db.treasury_transactions.insert_one(new_transaction.dict())
            transactions_created.extend(["expense", "income"])
            
        # Case 4: Converting from deferred to deferred (should not happen, but handle gracefully)
        # No treasury transactions needed
        
        # Update invoice payment method and remaining amount
        update_data = {"payment_method": new_payment_method}
        
        # Update remaining_amount based on new payment method
        if new_payment_method == "آجل":
            # Converting to deferred - set remaining_amount to total_amount
            update_data["remaining_amount"] = invoice_amount
        else:
            # Converting to immediate payment - set remaining_amount to 0
            update_data["remaining_amount"] = 0
            
        await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": update_data}
        )
        
        return {
            "message": f"تم تحويل طريقة الدفع من {old_payment_method} إلى {new_payment_method}",
            "old_method": old_payment_method,
            "new_method": new_payment_method,
            "amount_transferred": invoice_amount,
            "treasury_transactions_created": transactions_created,
            "remaining_amount_updated": update_data.get("remaining_amount", invoice.get("remaining_amount", 0))
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Cancel Invoice API
@api_router.delete("/invoices/{invoice_id}/cancel")
async def cancel_invoice(invoice_id: str, username: str = None):
    """Cancel invoice and restore materials to inventory"""
    try:
        # Find the invoice
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="الفاتورة غير موجودة")
        
        # Restore materials to inventory for each item
        for item in invoice.get("items", []):
            if item.get("product_type") == "manufactured":
                # Handle multi-material restoration
                if item.get("selected_materials"):
                    for material_info in item.get("selected_materials", []):
                        raw_material = await db.raw_materials.find_one({
                            "unit_code": material_info.get("unit_code"),
                            "inner_diameter": material_info.get("inner_diameter"),
                            "outer_diameter": material_info.get("outer_diameter")
                        })
                        
                        if raw_material:
                            seals_to_restore = material_info.get("seals_count", 0)
                            material_to_restore = seals_to_restore * (item.get("height", 0) + 2)
                            
                            # Add material back
                            await db.raw_materials.update_one(
                                {"id": raw_material["id"]},
                                {"$inc": {"height": material_to_restore}}
                            )
                            
                            print(f"✅ تم استرداد {material_to_restore} مم للخامة {raw_material.get('unit_code')}")
                
                # Handle single material restoration
                elif item.get("material_details"):
                    material_details = item.get("material_details")
                    raw_material = await db.raw_materials.find_one({
                        "unit_code": material_details.get("unit_code"),
                        "inner_diameter": material_details.get("inner_diameter"),
                        "outer_diameter": material_details.get("outer_diameter")
                    })
                    
                    if raw_material:
                        material_to_restore = item.get("quantity", 0) * (item.get("height", 0) + 2)
                        
                        # Add material back
                        await db.raw_materials.update_one(
                            {"id": raw_material["id"]},
                            {"$inc": {"height": material_to_restore}}
                        )
                        
                        print(f"✅ تم استرداد {material_to_restore} مم للخامة {raw_material.get('unit_code')}")
        
        # Remove treasury transaction if not deferred
        if invoice.get("payment_method") != "آجل":
            payment_method_mapping = {
                "نقدي": "cash",
                "آجل": "deferred",
                "فودافون كاش محمد الصاوي": "vodafone_elsawy",
                "فودافون كاش وائل محمد": "vodafone_wael", 
                "انستاباي": "instapay",
                "يد الصاوي": "yad_elsawy"
            }
            
            account_id = payment_method_mapping.get(invoice.get("payment_method"))
            if account_id:
                # Create negative transaction to reverse the income
                reversal_transaction = TreasuryTransaction(
                    account_id=account_id,
                    transaction_type="expense",
                    amount=invoice.get("total_amount", 0),
                    description=f"إلغاء فاتورة {invoice.get('invoice_number')}",
                    reference=f"إلغاء-{invoice.get('invoice_number')}",
                    balance=-invoice.get("total_amount", 0)
                )
                await db.treasury_transactions.insert_one(reversal_transaction.dict())
        
        # Remove invoice from database
        await db.invoices.delete_one({"id": invoice_id})
        
        # Remove from work orders
        await db.work_orders.update_many(
            {"invoices.id": invoice_id},
            {"$pull": {"invoices": {"id": invoice_id}}}
        )
        
        return {
            "message": f"تم إلغاء الفاتورة {invoice.get('invoice_number')} واسترداد المواد",
            "invoice_number": invoice.get("invoice_number"),
            "materials_restored": True,
            "treasury_reversed": invoice.get("payment_method") != "آجل"
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Business logic function for inventory transactions
async def create_inventory_transaction(transaction: InventoryTransactionCreate):
    """Create inventory transaction (in/out) - Business logic"""
    # Find inventory item by specifications if item_id not provided
    if not transaction.inventory_item_id:
        inventory_item = await db.inventory_items.find_one({
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
        inventory_item = await db.inventory_items.find_one({"id": transaction.inventory_item_id})
        if not inventory_item:
            raise HTTPException(status_code=404, detail="العنصر غير موجود في الجرد")
    
    # Check if there's enough stock for "out" transactions
    if transaction.transaction_type == "out" and abs(transaction.pieces_change) > inventory_item["available_pieces"]:
        raise HTTPException(
            status_code=400, 
            detail=f"المخزون غير كافي. المتاح: {inventory_item['available_pieces']} قطعة، المطلوب: {abs(transaction.pieces_change)} قطعة"
        )
    
    # Calculate new remaining pieces
    new_pieces = inventory_item["available_pieces"] + transaction.pieces_change
    if new_pieces < 0:
        new_pieces = 0
    
    # Create transaction
    transaction_obj = InventoryTransaction(
        **transaction.dict(),
        remaining_pieces=new_pieces
    )
    await db.inventory_transactions.insert_one(transaction_obj.dict())
    
    # Update inventory item
    await db.inventory_items.update_one(
        {"id": transaction.inventory_item_id},
        {
            "$set": {
                "available_pieces": new_pieces,
                "last_updated": datetime.utcnow()
            }
        }
    )
    
    transaction_dict = transaction_obj.dict()
    if "_id" in transaction_dict:
        del transaction_dict["_id"]
    return transaction_dict

@api_router.post("/inventory-transactions", response_model=InventoryTransaction)
async def create_inventory_transaction_api(transaction: InventoryTransactionCreate):
    """Create inventory transaction via API"""
    try:
        result = await create_inventory_transaction(transaction)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inventory/check-availability")
async def check_inventory_availability(
    material_type: MaterialType, 
    inner_diameter: float, 
    outer_diameter: float, 
    required_pieces: int
):
    """Check if material is available in inventory with required pieces"""
    try:
        inventory_item = await db.inventory_items.find_one({
            "material_type": material_type,
            "inner_diameter": inner_diameter,
            "outer_diameter": outer_diameter
        })
        
        if not inventory_item:
            return {
                "available": False,
                "message": f"المادة الخام غير متوفرة في الجرد: {material_type} - {inner_diameter}x{outer_diameter}",
                "available_pieces": 0,
                "required_pieces": required_pieces
            }
        
        available_pieces = inventory_item.get("available_pieces", 0)
        is_available = available_pieces >= required_pieces
        
        return {
            "available": is_available,
            "message": f"{'المادة متوفرة' if is_available else 'المادة غير متوفرة بالكمية المطلوبة'}",
            "available_pieces": available_pieces,
            "required_pieces": required_pieces,
            "inventory_item_id": inventory_item["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Excel Import/Export endpoints
@api_router.post("/excel/import/inventory")
async def import_inventory_excel(file: UploadFile = File(...)):
    """Import inventory items from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="يجب أن يكون الملف من نوع Excel (.xlsx أو .xls)")
        
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['material_type', 'inner_diameter', 'outer_diameter', 'available_pieces']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"أعمدة مفقودة: {', '.join(missing_columns)}")
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if item already exists
                existing_item = await db.inventory_items.find_one({
                    "material_type": row['material_type'],
                    "inner_diameter": float(row['inner_diameter']),
                    "outer_diameter": float(row['outer_diameter'])
                })
                
                if existing_item:
                    # Update existing item
                    await db.inventory_items.update_one(
                        {"id": existing_item["id"]},
                        {
                            "$set": {
                                "available_pieces": int(row['available_pieces']),
                                "min_stock_level": int(row.get('min_stock_level', 2)),
                                "notes": str(row.get('notes', '')),
                                "last_updated": datetime.utcnow()
                            }
                        }
                    )
                else:
                    # Create new item
                    inventory_item = InventoryItem(
                        material_type=row['material_type'],
                        inner_diameter=float(row['inner_diameter']),
                        outer_diameter=float(row['outer_diameter']),
                        available_pieces=int(row['available_pieces']),
                        min_stock_level=int(row.get('min_stock_level', 2)),
                        notes=str(row.get('notes', ''))
                    )
                    await db.inventory_items.insert_one(inventory_item.dict())
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"صف {index + 2}: {str(e)}")
        
        return {
            "message": f"تم استيراد {imported_count} عنصر بنجاح",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد الملف: {str(e)}")

@api_router.get("/excel/export/inventory")
async def export_inventory_excel():
    """Export inventory items to Excel file"""
    try:
        # Get all inventory items
        items = await db.inventory_items.find({}).to_list(None)
        
        if not items:
            raise HTTPException(status_code=404, detail="لا توجد عناصر جرد للتصدير")
        
        # Convert to DataFrame
        df_data = []
        for item in items:
            df_data.append({
                'material_type': item.get('material_type', ''),
                'inner_diameter': item.get('inner_diameter', 0),
                'outer_diameter': item.get('outer_diameter', 0),
                'available_pieces': item.get('available_pieces', 0),
                'min_stock_level': item.get('min_stock_level', 2),
                'notes': item.get('notes', ''),
                'created_at': item.get('created_at', ''),
                'last_updated': item.get('last_updated', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Inventory', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Inventory']
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        output.seek(0)
        
        # Return as streaming response
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"inventory_export_{current_date}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في تصدير الملف: {str(e)}")

@api_router.post("/excel/import/raw-materials")
async def import_raw_materials_excel(file: UploadFile = File(...)):
    """Import raw materials from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="يجب أن يكون الملف من نوع Excel (.xlsx أو .xls)")
        
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['material_type', 'inner_diameter', 'outer_diameter', 'height', 'pieces_count', 'unit_code', 'cost_per_mm']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"أعمدة مفقودة: {', '.join(missing_columns)}")
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                raw_material = RawMaterial(
                    material_type=row['material_type'],
                    inner_diameter=float(row['inner_diameter']),
                    outer_diameter=float(row['outer_diameter']),
                    height=float(row['height']),
                    pieces_count=int(row['pieces_count']),
                    unit_code=str(row['unit_code']),
                    cost_per_mm=float(row['cost_per_mm'])
                )
                await db.raw_materials.insert_one(raw_material.dict())
                imported_count += 1
                
            except Exception as e:
                errors.append(f"صف {index + 2}: {str(e)}")
        
        return {
            "message": f"تم استيراد {imported_count} مادة خام بنجاح",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد الملف: {str(e)}")

@api_router.get("/excel/export/raw-materials")
async def export_raw_materials_excel():
    """Export raw materials to Excel file"""
    try:
        # Get all raw materials
        materials = await db.raw_materials.find({}).to_list(None)
        
        if not materials:
            raise HTTPException(status_code=404, detail="لا توجد مواد خام للتصدير")
        
        # Convert to DataFrame
        df_data = []
        for material in materials:
            df_data.append({
                'material_type': material.get('material_type', ''),
                'inner_diameter': material.get('inner_diameter', 0),
                'outer_diameter': material.get('outer_diameter', 0),
                'height': material.get('height', 0),
                'pieces_count': material.get('pieces_count', 0),
                'unit_code': material.get('unit_code', ''),
                'cost_per_mm': material.get('cost_per_mm', 0),
                'created_at': material.get('created_at', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Raw Materials', index=False)
            
            # Get the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Raw Materials']
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        output.seek(0)
        
        # Return as streaming response
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"raw_materials_export_{current_date}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في تصدير الملف: {str(e)}")

# Bulk Import APIs for Data Management
@api_router.post("/raw-materials/bulk-import")
async def bulk_import_raw_materials(data: dict):
    """Bulk import raw materials from uploaded data"""
    try:
        imported_count = 0
        skipped_count = 0
        
        for item in data.get("data", []):
            try:
                # Check if material already exists
                existing = await db.raw_materials.find_one({"unit_code": item.get("unit_code")})
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new raw material directly without inventory checks for bulk import
                raw_material_dict = item.copy()
                if "id" not in raw_material_dict:
                    raw_material_dict["id"] = str(uuid.uuid4())
                if "created_at" not in raw_material_dict:
                    raw_material_dict["created_at"] = datetime.utcnow()
                
                await db.raw_materials.insert_one(raw_material_dict)
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing raw material: {e}")
                skipped_count += 1
        
        return {
            "message": f"تم استيراد {imported_count} مادة خام، تم تخطي {skipped_count} مادة",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد المواد الخام: {str(e)}")

@api_router.post("/invoices/bulk-import")
async def bulk_import_invoices(data: dict):
    """Bulk import invoices from uploaded data"""
    try:
        imported_count = 0
        skipped_count = 0
        
        for item in data.get("data", []):
            try:
                # Check if invoice already exists
                existing = await db.invoices.find_one({"invoice_number": item.get("invoice_number")})
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new invoice
                invoice = Invoice(**item)
                await db.invoices.insert_one(invoice.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing invoice: {e}")
                skipped_count += 1
        
        return {
            "message": f"تم استيراد {imported_count} فاتورة، تم تخطي {skipped_count} فاتورة",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد الفواتير: {str(e)}")

@api_router.post("/treasury/transactions/bulk-import")
async def bulk_import_treasury_transactions(data: dict):
    """Bulk import treasury transactions from uploaded data"""
    try:
        imported_count = 0
        skipped_count = 0
        
        for item in data.get("data", []):
            try:
                # Create new treasury transaction
                transaction = TreasuryTransaction(**item)
                await db.treasury_transactions.insert_one(transaction.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing treasury transaction: {e}")
                skipped_count += 1
        
        return {
            "message": f"تم استيراد {imported_count} معاملة خزينة، تم تخطي {skipped_count} معاملة",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد معاملات الخزينة: {str(e)}")

@api_router.post("/expenses/bulk-import")
async def bulk_import_expenses(data: dict):
    """Bulk import expenses from uploaded data"""
    try:
        imported_count = 0
        
        for item in data.get("data", []):
            try:
                # Create expense as treasury transaction
                expense_transaction = TreasuryTransaction(
                    account_id="cash",
                    transaction_type="expense",
                    amount=item.get("amount", 0),
                    description=item.get("description", "مصروف مستورد"),
                    reference=item.get("reference", "استيراد")
                )
                await db.treasury_transactions.insert_one(expense_transaction.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing expense: {e}")
        
        return {
            "message": f"تم استيراد {imported_count} مصروف",
            "imported": imported_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد المصروفات: {str(e)}")

@api_router.post("/revenues/bulk-import")  
async def bulk_import_revenues(data: dict):
    """Bulk import revenues from uploaded data"""
    try:
        imported_count = 0
        
        for item in data.get("data", []):
            try:
                # Create revenue as treasury transaction
                revenue_transaction = TreasuryTransaction(
                    account_id="cash",
                    transaction_type="income",
                    amount=item.get("amount", 0),
                    description=item.get("description", "إيراد مستورد"),
                    reference=item.get("reference", "استيراد")
                )
                await db.treasury_transactions.insert_one(revenue_transaction.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing revenue: {e}")
        
        return {
            "message": f"تم استيراد {imported_count} إيراد",
            "imported": imported_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد الإيرادات: {str(e)}")

@api_router.post("/work-orders/bulk-import")
async def bulk_import_work_orders(data: dict):
    """Bulk import work orders from uploaded data"""
    try:
        imported_count = 0
        skipped_count = 0
        
        for item in data.get("data", []):
            try:
                # Check if work order already exists
                existing = await db.work_orders.find_one({"invoice_id": item.get("invoice_id")})
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new work order
                work_order = WorkOrder(**item)
                await db.work_orders.insert_one(work_order.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing work order: {e}")
                skipped_count += 1
        
        return {
            "message": f"تم استيراد {imported_count} أمر شغل، تم تخطي {skipped_count} أمر",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد أوامر الشغل: {str(e)}")

@api_router.post("/pricing/bulk-import")
async def bulk_import_pricing(data: dict):
    """Bulk import pricing data from uploaded data"""
    try:
        imported_count = 0
        skipped_count = 0
        
        for item in data.get("data", []):
            try:
                # Check if pricing rule already exists
                existing = await db.pricing.find_one({
                    "client_type": item.get("client_type"),
                    "material_type": item.get("material_type")
                })
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new pricing rule
                pricing = Pricing(**item)
                await db.pricing.insert_one(pricing.dict())
                imported_count += 1
                
            except Exception as e:
                print(f"Error importing pricing: {e}")
                skipped_count += 1
        
        return {
            "message": f"تم استيراد {imported_count} قاعدة تسعير، تم تخطي {skipped_count} قاعدة",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في استيراد قواعد التسعير: {str(e)}")

# Complete Data Export API
@api_router.get("/data-management/export-all")
async def export_all_data():
    """Export all system data for backup/transfer"""
    try:
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "system_version": "Master Seal v1.0",
            "data": {}
        }
        
        # Helper function to clean MongoDB ObjectIds
        def clean_mongo_data(data_list):
            cleaned = []
            for item in data_list:
                if "_id" in item:
                    del item["_id"]
                cleaned.append(item)
            return cleaned
        
        # Export all data types with ObjectId cleanup
        raw_materials = await db.raw_materials.find().to_list(length=None)
        export_data["data"]["raw_materials"] = clean_mongo_data(raw_materials)
        
        invoices = await db.invoices.find().to_list(length=None)
        export_data["data"]["invoices"] = clean_mongo_data(invoices)
        
        treasury_transactions = await db.treasury_transactions.find().to_list(length=None)
        export_data["data"]["treasury_transactions"] = clean_mongo_data(treasury_transactions)
        
        work_orders = await db.work_orders.find().to_list(length=None)
        export_data["data"]["work_orders"] = clean_mongo_data(work_orders)
        
        pricing = await db.pricing.find().to_list(length=None)
        export_data["data"]["pricing"] = clean_mongo_data(pricing)
        
        # Add other collections
        customers = await db.customers.find().to_list(length=None)
        export_data["data"]["customers"] = clean_mongo_data(customers)
        
        expenses = await db.expenses.find().to_list(length=None)
        export_data["data"]["expenses"] = clean_mongo_data(expenses)
        
        return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في تصدير البيانات: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)