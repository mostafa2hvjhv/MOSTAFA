import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, null, {
        params: { username, password }
      });
      
      if (response.data.success) {
        setUser(response.data.user);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="text-xl">جاري التحميل...</div>
    </div>;
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const success = await login(username, password);
    if (!success) {
      setError('خطأ في اسم المستخدم أو كلمة المرور');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center" dir="rtl">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-blue-600">ماستر سيل</h1>
          <p className="text-gray-600">نظام إدارة الشركة</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              اسم المستخدم
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              كلمة المرور
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}
          
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            دخول
          </button>
        </form>
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = ({ currentPage, onPageChange }) => {
  const { user, logout } = useAuth();
  
  const adminPages = [
    { key: 'dashboard', label: 'لوحة التحكم' },
    { key: 'sales', label: 'المبيعات' },
    { key: 'inventory', label: 'المخزون' },
    { key: 'deferred', label: 'الآجل' },
    { key: 'expenses', label: 'المصروفات' },
    { key: 'revenue', label: 'الإيرادات' },
    { key: 'invoices', label: 'الفواتير' },
    { key: 'work-orders', label: 'أمر شغل' },
    { key: 'users', label: 'المستخدمين' }
  ];
  
  const userPages = [
    { key: 'dashboard', label: 'لوحة التحكم' },
    { key: 'sales', label: 'المبيعات' },
    { key: 'inventory', label: 'المخزون' },
    { key: 'deferred', label: 'الآجل' },
    { key: 'expenses', label: 'المصروفات' },
    { key: 'work-orders', label: 'أمر شغل' }
  ];
  
  const pages = user?.role === 'admin' ? adminPages : userPages;

  return (
    <nav className="bg-blue-600 text-white" dir="rtl">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4 space-x-reverse">
            <h1 className="text-xl font-bold">ماستر سيل</h1>
            <span className="text-sm">الحرفيان شارع السوبر جيت - 01020630677</span>
          </div>
          
          <div className="flex items-center space-x-4 space-x-reverse">
            <span className="text-sm">أهلاً {user?.username}</span>
            <button
              onClick={logout}
              className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm"
            >
              خروج
            </button>
          </div>
        </div>
        
        <div className="flex space-x-4 space-x-reverse border-t border-blue-500 py-2">
          {pages.map(page => (
            <button
              key={page.key}
              onClick={() => onPageChange(page.key)}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                currentPage === page.key 
                  ? 'bg-blue-800 text-white' 
                  : 'hover:bg-blue-500'
              }`}
            >
              {page.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState({
    total_sales: 0,
    total_expenses: 0,
    net_profit: 0,
    total_unpaid: 0,
    invoice_count: 0,
    customer_count: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const clearAllData = () => {
    if (!confirm('هل أنت متأكد من حذف جميع البيانات؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    // Reset dashboard stats
    setStats({
      total_sales: 0,
      total_expenses: 0,
      net_profit: 0,
      total_unpaid: 0,
      invoice_count: 0,
      customer_count: 0
    });
    
    alert('تم حذف جميع البيانات');
  };

  const printReport = (reportType) => {
    const currentDate = new Date().toLocaleDateString('ar-EG');
    let printContent = `
      <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h1>ماستر سيل</h1>
          <p>الحرفيان شارع السوبر جيت - 01020630677</p>
          <h2>تقرير لوحة التحكم</h2>
          <p>التاريخ: ${currentDate}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>إجمالي المبيعات:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">ج.م ${stats.total_sales.toFixed(2)}</td>
          </tr>
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>إجمالي المصروفات:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">ج.م ${stats.total_expenses.toFixed(2)}</td>
          </tr>
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>صافي الربح:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">ج.م ${stats.net_profit.toFixed(2)}</td>
          </tr>
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>المبالغ المستحقة:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">ج.م ${stats.total_unpaid.toFixed(2)}</td>
          </tr>
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>عدد الفواتير:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">${stats.invoice_count}</td>
          </tr>
          <tr>
            <td style="border: 1px solid #ddd; padding: 10px;"><strong>عدد العملاء:</strong></td>
            <td style="border: 1px solid #ddd; padding: 10px;">${stats.customer_count}</td>
          </tr>
        </table>
      </div>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">لوحة التحكم</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => printReport('dashboard')}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">إجمالي المبيعات</h3>
          <p className="text-3xl font-bold text-green-600 text-center">
            ج.م {stats.total_sales.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">إجمالي المصروفات</h3>
          <p className="text-3xl font-bold text-red-600 text-center">
            ج.م {stats.total_expenses.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">صافي الربح</h3>
          <p className="text-3xl font-bold text-blue-600 text-center">
            ج.م {stats.net_profit.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">المبالغ المستحقة</h3>
          <p className="text-3xl font-bold text-orange-600 text-center">
            ج.م {stats.total_unpaid.toFixed(2)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">عدد الفواتير</h3>
          <p className="text-3xl font-bold text-purple-600 text-center">
            {stats.invoice_count}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 text-center">عدد العملاء</h3>
          <p className="text-3xl font-bold text-blue-600 text-center">
            {stats.customer_count}
          </p>
        </div>
      </div>
    </div>
  );
};

// Sales Component
const Sales = () => {
  const [customers, setCustomers] = useState([]);
  const [newCustomer, setNewCustomer] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [currentItem, setCurrentItem] = useState({
    seal_type: 'RSL',
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    height: '',
    quantity: 1,
    unit_price: ''
  });
  const [items, setItems] = useState([]);
  const [paymentMethod, setPaymentMethod] = useState('نقدي');
  const [compatibilityResults, setCompatibilityResults] = useState(null);
  const [selectedMaterial, setSelectedMaterial] = useState(null);

  const sealTypes = ['RSL', 'RS', 'RSE', 'B17', 'B3', 'B14', 'B1', 'R15', 'R17', 'W1', 'W4', 'W5', 'W11', 'WBT', 'XR', 'CH', 'VR'];
  const materialTypes = ['NBR', 'BUR', 'BT', 'VT', 'BOOM'];

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const checkCompatibility = async () => {
    try {
      const response = await axios.post(`${API}/compatibility-check`, {
        seal_type: currentItem.seal_type,
        inner_diameter: parseFloat(currentItem.inner_diameter),
        outer_diameter: parseFloat(currentItem.outer_diameter),
        height: parseFloat(currentItem.height)
      });
      setCompatibilityResults(response.data);
    } catch (error) {
      console.error('Error checking compatibility:', error);
    }
  };

  const addItem = () => {
    if (!currentItem.inner_diameter || !currentItem.outer_diameter || !currentItem.height || !currentItem.unit_price) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    const item = {
      ...currentItem,
      inner_diameter: parseFloat(currentItem.inner_diameter),
      outer_diameter: parseFloat(currentItem.outer_diameter),
      height: parseFloat(currentItem.height),
      quantity: parseInt(currentItem.quantity),
      unit_price: parseFloat(currentItem.unit_price),
      total_price: parseFloat(currentItem.unit_price) * parseInt(currentItem.quantity),
      material_used: selectedMaterial ? selectedMaterial.unit_code : null
    };

    setItems([...items, item]);
    setCurrentItem({
      seal_type: 'RSL',
      material_type: 'NBR',
      inner_diameter: '',
      outer_diameter: '',
      height: '',
      quantity: 1,
      unit_price: ''
    });
    setCompatibilityResults(null);
    setSelectedMaterial(null);
  };

  const createInvoice = async () => {
    if (!selectedCustomer && !newCustomer) {
      alert('الرجاء اختيار العميل أو إدخال اسم عميل جديد');
      return;
    }

    if (items.length === 0) {
      alert('الرجاء إضافة منتجات للفاتورة');
      return;
    }

    try {
      let customerId = selectedCustomer;
      let customerName = '';

      // إنشاء عميل جديد إذا لزم الأمر
      if (!selectedCustomer && newCustomer) {
        const customerResponse = await axios.post(`${API}/customers`, {
          name: newCustomer,
          phone: '',
          address: ''
        });
        customerId = customerResponse.data.id;
        customerName = newCustomer;
        
        // تحديث قائمة العملاء
        fetchCustomers();
      } else {
        const customer = customers.find(c => c.id === customerId);
        customerName = customer ? customer.name : '';
      }

      // إنشاء الفاتورة
      const invoiceData = {
        customer_id: customerId,
        customer_name: customerName,
        items: items,
        payment_method: paymentMethod,
        notes: ''
      };

      const response = await axios.post(`${API}/invoices`, invoiceData);
      
      if (response.data) {
        alert('تم إنشاء الفاتورة بنجاح');
        
        // مسح البيانات
        setItems([]);
        setSelectedCustomer('');
        setNewCustomer('');
        setPaymentMethod('نقدي');
        
        // طباعة الفاتورة
        printInvoice(response.data);
      }
    } catch (error) {
      console.error('Error creating invoice:', error);
      alert('حدث خطأ في إنشاء الفاتورة');
    }
  };

  const printInvoice = (invoice) => {
    const printContent = `
      <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h1>ماستر سيل</h1>
          <p>الحرفيان شارع السوبر جيت - 01020630677</p>
        </div>
        <div style="margin-bottom: 20px;">
          <strong>رقم الفاتورة:</strong> ${invoice.invoice_number}<br>
          <strong>العميل:</strong> ${invoice.customer_name}<br>
          <strong>التاريخ:</strong> ${new Date(invoice.date).toLocaleDateString('ar-EG')}<br>
          <strong>طريقة الدفع:</strong> ${invoice.payment_method}
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #f0f0f0;">
              <th style="border: 1px solid #ddd; padding: 8px;">المنتج</th>
              <th style="border: 1px solid #ddd; padding: 8px;">الكمية</th>
              <th style="border: 1px solid #ddd; padding: 8px;">السعر</th>
              <th style="border: 1px solid #ddd; padding: 8px;">المجموع</th>
            </tr>
          </thead>
          <tbody>
            ${invoice.items.map(item => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">
                  ${item.seal_type} - ${item.material_type}<br>
                  ${item.inner_diameter} × ${item.outer_diameter} × ${item.height}
                </td>
                <td style="border: 1px solid #ddd; padding: 8px;">${item.quantity}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">ج.م ${item.unit_price}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">ج.م ${item.total_price}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div style="text-align: left;">
          <strong>الإجمالي: ج.م ${invoice.total_amount}</strong>
        </div>
      </div>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="p-6" dir="rtl">
      <h2 className="text-2xl font-bold text-blue-600 mb-6">المبيعات</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Selection */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">اختيار العميل</h3>
          
          <div className="space-y-4">
            <div>
              <select
                value={selectedCustomer}
                onChange={(e) => setSelectedCustomer(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">اختر العميل</option>
                {customers.map(customer => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex space-x-2 space-x-reverse">
              <input
                type="text"
                value={newCustomer}
                onChange={(e) => setNewCustomer(e.target.value)}
                placeholder="اسم عميل جديد"
                className="flex-1 p-2 border border-gray-300 rounded"
              />
              <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                عميل جديد
              </button>
            </div>
          </div>
        </div>

        {/* Product Entry */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">إضافة منتج</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">نوع السيل</label>
              <select
                value={currentItem.seal_type}
                onChange={(e) => setCurrentItem({...currentItem, seal_type: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {sealTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">نوع الخامة</label>
              <select
                value={currentItem.material_type}
                onChange={(e) => setCurrentItem({...currentItem, material_type: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {materialTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">القطر الداخلي</label>
              <input
                type="number"
                value={currentItem.inner_diameter}
                onChange={(e) => setCurrentItem({...currentItem, inner_diameter: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">القطر الخارجي</label>
              <input
                type="number"
                value={currentItem.outer_diameter}
                onChange={(e) => setCurrentItem({...currentItem, outer_diameter: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">ارتفاع السيل</label>
              <input
                type="number"
                value={currentItem.height}
                onChange={(e) => setCurrentItem({...currentItem, height: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">عدد السيل</label>
              <input
                type="number"
                value={currentItem.quantity}
                onChange={(e) => setCurrentItem({...currentItem, quantity: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">سعر السيل الواحد</label>
              <input
                type="number"
                step="0.01"
                value={currentItem.unit_price}
                onChange={(e) => setCurrentItem({...currentItem, unit_price: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div className="flex items-end">
              <button
                onClick={checkCompatibility}
                className="w-full bg-yellow-500 text-white p-2 rounded hover:bg-yellow-600"
              >
                فحص التوافق
              </button>
            </div>
          </div>
          
          <button
            onClick={addItem}
            className="w-full bg-green-500 text-white p-2 rounded hover:bg-green-600 mt-4"
          >
            إضافة للفاتورة
          </button>
        </div>
      </div>

      {/* Compatibility Results */}
      {compatibilityResults && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">نتائج فحص التوافق</h3>
          
          {compatibilityResults.compatible_materials.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium mb-2">الخامات المتوافقة:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {compatibilityResults.compatible_materials.map((material, index) => (
                  <div
                    key={index}
                    className={`p-3 border rounded cursor-pointer transition-colors ${
                      selectedMaterial?.unit_code === material.unit_code 
                        ? 'border-blue-500 bg-blue-50' 
                        : material.low_stock 
                          ? 'border-red-300 bg-red-50 hover:bg-red-100' 
                          : 'border-green-300 bg-green-50 hover:bg-green-100'
                    }`}
                    onClick={() => setSelectedMaterial(material)}
                  >
                    <p><strong>النوع:</strong> {material.material_type}</p>
                    <p><strong>الكود:</strong> {material.unit_code}</p>
                    <p><strong>المقاس:</strong> {material.inner_diameter} × {material.outer_diameter} × {material.height}</p>
                    <p><strong>عدد القطع:</strong> {material.pieces_count}</p>
                    {material.warning && <p className="text-red-600 text-sm">{material.warning}</p>}
                    {selectedMaterial?.unit_code === material.unit_code && (
                      <p className="text-blue-600 font-semibold text-sm mt-2">✓ محدد للاستخدام</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {compatibilityResults.compatible_products.length > 0 && (
            <div>
              <h4 className="font-medium mb-2">المنتجات الجاهزة:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {compatibilityResults.compatible_products.map((product, index) => (
                  <div 
                    key={index} 
                    className="p-3 border border-blue-300 bg-blue-50 rounded cursor-pointer hover:bg-blue-100"
                    onClick={() => setSelectedMaterial({
                      unit_code: `FINISHED-${product.id}`,
                      material_type: product.material_type,
                      seal_type: product.seal_type
                    })}
                  >
                    <p><strong>النوع:</strong> {product.seal_type} - {product.material_type}</p>
                    <p><strong>المقاس:</strong> {product.inner_diameter} × {product.outer_diameter} × {product.height}</p>
                    <p><strong>الكمية:</strong> {product.quantity}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedMaterial && (
            <div className="mt-4 p-3 bg-blue-100 rounded">
              <p className="font-semibold text-blue-800">
                تم اختيار الخامة: {selectedMaterial.unit_code} ({selectedMaterial.material_type})
              </p>
            </div>
          )}
        </div>
      )}

      {/* Current Items */}
      {items.length > 0 && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">الفواتير الأخيرة</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-2">نوع السيل</th>
                  <th className="border border-gray-300 p-2">نوع الخامة</th>
                  <th className="border border-gray-300 p-2">المقاس</th>
                  <th className="border border-gray-300 p-2">الكمية</th>
                  <th className="border border-gray-300 p-2">السعر</th>
                  <th className="border border-gray-300 p-2">المجموع</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={index}>
                    <td className="border border-gray-300 p-2">{item.seal_type}</td>
                    <td className="border border-gray-300 p-2">{item.material_type}</td>
                    <td className="border border-gray-300 p-2">
                      {item.inner_diameter} × {item.outer_diameter} × {item.height}
                    </td>
                    <td className="border border-gray-300 p-2">{item.quantity}</td>
                    <td className="border border-gray-300 p-2">ج.م {item.unit_price}</td>
                    <td className="border border-gray-300 p-2">ج.م {item.total_price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 flex justify-between items-center">
            <div>
              <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="p-2 border border-gray-300 rounded"
              >
                <option value="نقدي">نقدي</option>
                <option value="آجل">آجل</option>
                <option value="فودافون كاش محمد الصاوي">فودافون كاش محمد الصاوي</option>
                <option value="فودافون كاش وائل محمد">فودافون كاش وائل محمد</option>
                <option value="انستاباي">انستاباي</option>
              </select>
            </div>
            
            <div className="text-xl font-bold">
              الإجمالي: ج.م {items.reduce((sum, item) => sum + item.total_price, 0).toFixed(2)}
            </div>
          </div>
          
          <button
            onClick={createInvoice}
            className="w-full bg-green-500 text-white p-3 rounded hover:bg-green-600 mt-4 text-lg font-semibold"
          >
            إنشاء الفاتورة
          </button>
        </div>
      )}
    </div>
  );
};

// Simple placeholder components for other pages
// Inventory Component
const Inventory = () => {
  const [rawMaterials, setRawMaterials] = useState([]);
  const [finishedProducts, setFinishedProducts] = useState([]);
  const [newRawMaterial, setNewRawMaterial] = useState({
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    height: '',
    pieces_count: '',
    unit_code: '',
    cost_per_mm: ''
  });
  const [newFinishedProduct, setNewFinishedProduct] = useState({
    seal_type: 'RSL',
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    height: '',
    quantity: '',
    unit_price: ''
  });

  const materialTypes = ['NBR', 'BUR', 'BT', 'VT', 'BOOM'];
  const sealTypes = ['RSL', 'RS', 'RSE', 'B17', 'B3', 'B14', 'B1', 'R15', 'R17', 'W1', 'W4', 'W5', 'W11', 'WBT', 'XR', 'CH', 'VR'];

  useEffect(() => {
    fetchRawMaterials();
    fetchFinishedProducts();
  }, []);

  const fetchRawMaterials = async () => {
    try {
      const response = await axios.get(`${API}/raw-materials`);
      setRawMaterials(response.data);
    } catch (error) {
      console.error('Error fetching raw materials:', error);
    }
  };

  const fetchFinishedProducts = async () => {
    try {
      const response = await axios.get(`${API}/finished-products`);
      setFinishedProducts(response.data);
    } catch (error) {
      console.error('Error fetching finished products:', error);
    }
  };

  const addRawMaterial = async () => {
    if (!newRawMaterial.inner_diameter || !newRawMaterial.outer_diameter || !newRawMaterial.height || !newRawMaterial.pieces_count || !newRawMaterial.unit_code || !newRawMaterial.cost_per_mm) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      await axios.post(`${API}/raw-materials`, {
        ...newRawMaterial,
        inner_diameter: parseFloat(newRawMaterial.inner_diameter),
        outer_diameter: parseFloat(newRawMaterial.outer_diameter),
        height: parseFloat(newRawMaterial.height),
        pieces_count: parseInt(newRawMaterial.pieces_count),
        cost_per_mm: parseFloat(newRawMaterial.cost_per_mm)
      });

      setNewRawMaterial({
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        pieces_count: '',
        unit_code: '',
        cost_per_mm: ''
      });

      fetchRawMaterials();
      alert('تم إضافة المادة الخام بنجاح');
    } catch (error) {
      console.error('Error adding raw material:', error);
      alert('حدث خطأ في إضافة المادة الخام');
    }
  };

  const addFinishedProduct = async () => {
    if (!newFinishedProduct.inner_diameter || !newFinishedProduct.outer_diameter || !newFinishedProduct.height || !newFinishedProduct.quantity || !newFinishedProduct.unit_price) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      await axios.post(`${API}/finished-products`, {
        ...newFinishedProduct,
        inner_diameter: parseFloat(newFinishedProduct.inner_diameter),
        outer_diameter: parseFloat(newFinishedProduct.outer_diameter),
        height: parseFloat(newFinishedProduct.height),
        quantity: parseInt(newFinishedProduct.quantity),
        unit_price: parseFloat(newFinishedProduct.unit_price)
      });

      setNewFinishedProduct({
        seal_type: 'RSL',
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        quantity: '',
        unit_price: ''
      });

      fetchFinishedProducts();
      alert('تم إضافة المنتج الجاهز بنجاح');
    } catch (error) {
      console.error('Error adding finished product:', error);
      alert('حدث خطأ في إضافة المنتج الجاهز');
    }
  };

  const deleteRawMaterial = async (materialId) => {
    if (!confirm('هل أنت متأكد من حذف هذه المادة؟')) return;

    try {
      await axios.delete(`${API}/raw-materials/${materialId}`);
      fetchRawMaterials();
      alert('تم حذف المادة بنجاح');
    } catch (error) {
      console.error('Error deleting material:', error);
      alert('حدث خطأ في حذف المادة');
    }
  };

  const printReport = (reportType) => {
    window.print();
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">إدارة المخزون</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={() => { fetchRawMaterials(); fetchFinishedProducts(); }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => printReport('inventory')}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Raw Materials Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">إضافة مادة خام جديدة</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">نوع الخامة</label>
            <select
              value={newRawMaterial.material_type}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, material_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {materialTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الداخلي</label>
            <input
              type="number"
              value={newRawMaterial.inner_diameter}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, inner_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الخارجي</label>
            <input
              type="number"
              value={newRawMaterial.outer_diameter}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, outer_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الارتفاع المتاح (ملي)</label>
            <input
              type="number"
              value={newRawMaterial.height}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, height: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">عدد القطع</label>
            <input
              type="number"
              value={newRawMaterial.pieces_count}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, pieces_count: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">كود الوحدة</label>
            <input
              type="text"
              value={newRawMaterial.unit_code}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, unit_code: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">تكلفة الملي الواحد</label>
            <input
              type="number"
              step="0.01"
              value={newRawMaterial.cost_per_mm}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, cost_per_mm: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        </div>
        
        <button
          onClick={addRawMaterial}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
        >
          إضافة المادة الخام
        </button>
      </div>

      {/* Raw Materials List */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">المواد الخام الموجودة</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">نوع الخامة</th>
                <th className="border border-gray-300 p-2">القطر الداخلي</th>
                <th className="border border-gray-300 p-2">القطر الخارجي</th>
                <th className="border border-gray-300 p-2">الارتفاع المتاح</th>
                <th className="border border-gray-300 p-2">عدد القطع</th>
                <th className="border border-gray-300 p-2">كود الوحدة</th>
                <th className="border border-gray-300 p-2">تكلفة الملي</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {rawMaterials.map((material) => (
                <tr 
                  key={material.id} 
                  className={material.height < 20 ? 'bg-red-100' : ''}
                >
                  <td className="border border-gray-300 p-2">{material.material_type}</td>
                  <td className="border border-gray-300 p-2">{material.inner_diameter}</td>
                  <td className="border border-gray-300 p-2">{material.outer_diameter}</td>
                  <td className="border border-gray-300 p-2">
                    <span className={material.height < 20 ? 'text-red-600 font-bold' : ''}>
                      {material.height} ملي
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">{material.pieces_count}</td>
                  <td className="border border-gray-300 p-2">{material.unit_code}</td>
                  <td className="border border-gray-300 p-2">ج.م {material.cost_per_mm}</td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600">
                        تعديل
                      </button>
                      <button 
                        onClick={() => deleteRawMaterial(material.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600">
                        حذف
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Finished Products Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">مخزون الإنتاج التام</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">نوع السيل</label>
            <select
              value={newFinishedProduct.seal_type}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, seal_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {sealTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">نوع الخامة</label>
            <select
              value={newFinishedProduct.material_type}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, material_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {materialTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الداخلي</label>
            <input
              type="number"
              value={newFinishedProduct.inner_diameter}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, inner_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الخارجي</label>
            <input
              type="number"
              value={newFinishedProduct.outer_diameter}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, outer_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الارتفاع</label>
            <input
              type="number"
              value={newFinishedProduct.height}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, height: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الكمية</label>
            <input
              type="number"
              value={newFinishedProduct.quantity}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, quantity: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">سعر الوحدة</label>
            <input
              type="number"
              step="0.01"
              value={newFinishedProduct.unit_price}
              onChange={(e) => setNewFinishedProduct({...newFinishedProduct, unit_price: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        </div>
        
        <button
          onClick={addFinishedProduct}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
        >
          إضافة منتج جاهز
        </button>
      </div>

      {/* Finished Products List */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">المنتجات الجاهزة</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">نوع السيل</th>
                <th className="border border-gray-300 p-2">نوع الخامة</th>
                <th className="border border-gray-300 p-2">المقاس</th>
                <th className="border border-gray-300 p-2">الكمية</th>
                <th className="border border-gray-300 p-2">سعر الوحدة</th>
                <th className="border border-gray-300 p-2">القيمة الإجمالية</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {finishedProducts.map((product) => (
                <tr key={product.id}>
                  <td className="border border-gray-300 p-2">{product.seal_type}</td>
                  <td className="border border-gray-300 p-2">{product.material_type}</td>
                  <td className="border border-gray-300 p-2">
                    {product.inner_diameter} × {product.outer_diameter} × {product.height}
                  </td>
                  <td className="border border-gray-300 p-2">{product.quantity}</td>
                  <td className="border border-gray-300 p-2">ج.م {product.unit_price}</td>
                  <td className="border border-gray-300 p-2">ج.م {(product.quantity * product.unit_price).toFixed(2)}</td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600">
                        تعديل
                      </button>
                      <button className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600">
                        حذف
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Deferred Payments Component
const Deferred = () => {
  const [unpaidInvoices, setUnpaidInvoices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('نقدي');
  const [paymentNotes, setPaymentNotes] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  useEffect(() => {
    fetchUnpaidInvoices();
    fetchCustomers();
  }, []);

  const fetchUnpaidInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      const invoices = response.data.filter(invoice => 
        invoice.status === 'غير مدفوعة' || invoice.status === 'مدفوعة جزئياً'
      );
      setUnpaidInvoices(invoices);
    } catch (error) {
      console.error('Error fetching unpaid invoices:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const getCustomerName = (customerId) => {
    const customer = customers.find(c => c.id === customerId);
    return customer ? customer.name : 'عميل غير محدد';
  };

  const makePayment = async () => {
    if (!selectedInvoice || !paymentAmount) {
      alert('الرجاء اختيار الفاتورة وإدخال المبلغ');
      return;
    }

    if (parseFloat(paymentAmount) > selectedInvoice.remaining_amount) {
      alert('المبلغ المدخل أكبر من المبلغ المستحق');
      return;
    }

    try {
      await axios.post(`${API}/payments`, {
        invoice_id: selectedInvoice.id,
        amount: parseFloat(paymentAmount),
        payment_method: paymentMethod,
        notes: paymentNotes
      });

      setPaymentAmount('');
      setPaymentNotes('');
      setSelectedInvoice(null);
      fetchUnpaidInvoices();
      alert('تم تسجيل الدفعة بنجاح');
    } catch (error) {
      console.error('Error making payment:', error);
      alert('حدث خطأ في تسجيل الدفعة');
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">الآجل - متابعة المدفوعات</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={fetchUnpaidInvoices}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Payment Form */}
      {selectedInvoice && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h3 className="text-lg font-semibold mb-4">تسجيل دفعة</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">رقم الفاتورة</label>
              <input
                type="text"
                value={selectedInvoice.invoice_number}
                disabled
                className="w-full p-2 border border-gray-300 rounded bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">العميل</label>
              <input
                type="text"
                value={selectedInvoice.customer_name}
                disabled
                className="w-full p-2 border border-gray-300 rounded bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">المبلغ المستحق</label>
              <input
                type="text"
                value={`ج.م ${selectedInvoice.remaining_amount?.toFixed(2) || '0.00'}`}
                disabled
                className="w-full p-2 border border-gray-300 rounded bg-gray-100"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">مبلغ الدفعة</label>
              <input
                type="number"
                step="0.01"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="0.00"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="نقدي">نقدي</option>
                <option value="فودافون كاش محمد الصاوي">فودافون كاش محمد الصاوي</option>
                <option value="فودافون كاش وائل محمد">فودافون كاش وائل محمد</option>
                <option value="انستاباي">انستاباي</option>
              </select>
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">ملاحظات</label>
              <input
                type="text"
                value={paymentNotes}
                onChange={(e) => setPaymentNotes(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
                placeholder="ملاحظات إضافية (اختياري)"
              />
            </div>
          </div>
          
          <div className="flex space-x-4 space-x-reverse">
            <button
              onClick={makePayment}
              className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
            >
              تسجيل الدفعة
            </button>
            <button
              onClick={() => setSelectedInvoice(null)}
              className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}

      {/* Unpaid Invoices */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">الفواتير غير المسددة</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">رقم الفاتورة</th>
                <th className="border border-gray-300 p-2">العميل</th>
                <th className="border border-gray-300 p-2">التاريخ</th>
                <th className="border border-gray-300 p-2">الإجمالي</th>
                <th className="border border-gray-300 p-2">المدفوع</th>
                <th className="border border-gray-300 p-2">المستحق</th>
                <th className="border border-gray-300 p-2">الحالة</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {unpaidInvoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="border border-gray-300 p-2">{invoice.invoice_number}</td>
                  <td className="border border-gray-300 p-2">{invoice.customer_name}</td>
                  <td className="border border-gray-300 p-2">
                    {new Date(invoice.date).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="border border-gray-300 p-2">ج.م {invoice.total_amount?.toFixed(2) || '0.00'}</td>
                  <td className="border border-gray-300 p-2">ج.م {invoice.paid_amount?.toFixed(2) || '0.00'}</td>
                  <td className="border border-gray-300 p-2">
                    <span className="font-bold text-red-600">
                      ج.م {invoice.remaining_amount?.toFixed(2) || '0.00'}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      invoice.status === 'غير مدفوعة' ? 'bg-red-100 text-red-800' :
                      invoice.status === 'مدفوعة جزئياً' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {invoice.status}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button
                        onClick={() => setSelectedInvoice(invoice)}
                        className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                      >
                        عرض الدفعات
                      </button>
                      <button
                        onClick={() => setSelectedInvoice(invoice)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                      >
                        دفع
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {unpaidInvoices.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              لا توجد فواتير غير مسددة
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-red-50 p-4 rounded">
            <h4 className="font-semibold text-red-800">إجمالي المبالغ المستحقة</h4>
            <p className="text-2xl font-bold text-red-600">
              ج.م {unpaidInvoices.reduce((sum, inv) => sum + (inv.remaining_amount || 0), 0).toFixed(2)}
            </p>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded">
            <h4 className="font-semibold text-yellow-800">عدد الفواتير المعلقة</h4>
            <p className="text-2xl font-bold text-yellow-600">{unpaidInvoices.length}</p>
          </div>
          
          <div className="bg-blue-50 p-4 rounded">
            <h4 className="font-semibold text-blue-800">إجمالي المبلغ الأصلي</h4>
            <p className="text-2xl font-bold text-blue-600">
              ج.م {unpaidInvoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0).toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Expenses Component
const Expenses = () => {
  const [expenses, setExpenses] = useState([]);
  const [newExpense, setNewExpense] = useState({
    description: '',
    amount: '',
    category: 'خامات'
  });

  const expenseCategories = ['خامات', 'رواتب', 'كهرباء', 'صيانة', 'أخرى'];

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const response = await axios.get(`${API}/expenses`);
      setExpenses(response.data);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    }
  };

  const addExpense = async () => {
    if (!newExpense.description || !newExpense.amount) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      await axios.post(`${API}/expenses`, {
        ...newExpense,
        amount: parseFloat(newExpense.amount)
      });

      setNewExpense({
        description: '',
        amount: '',
        category: 'خامات'
      });

      fetchExpenses();
      alert('تم إضافة المصروف بنجاح');
    } catch (error) {
      console.error('Error adding expense:', error);
      alert('حدث خطأ في إضافة المصروف');
    }
  };

  const deleteExpense = async (expenseId) => {
    if (!confirm('هل أنت متأكد من حذف هذا المصروف؟')) return;

    try {
      await axios.delete(`${API}/expenses/${expenseId}`);
      fetchExpenses();
      alert('تم حذف المصروف بنجاح');
    } catch (error) {
      console.error('Error deleting expense:', error);
      alert('حدث خطأ في حذف المصروف');
    }
  };

  const getTotalExpenses = () => {
    return expenses.reduce((sum, expense) => sum + expense.amount, 0);
  };

  const getExpensesByCategory = () => {
    const byCategory = {};
    expenseCategories.forEach(cat => {
      byCategory[cat] = expenses
        .filter(exp => exp.category === cat)
        .reduce((sum, exp) => sum + exp.amount, 0);
    });
    return byCategory;
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">المصروفات</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={fetchExpenses}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Add New Expense */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">إضافة مصروف جديد</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">وصف المصروف</label>
            <input
              type="text"
              value={newExpense.description}
              onChange={(e) => setNewExpense({...newExpense, description: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="مثال: شراء خامات، كهرباء المصنع"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">المبلغ</label>
            <input
              type="number"
              step="0.01"
              value={newExpense.amount}
              onChange={(e) => setNewExpense({...newExpense, amount: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="0.00"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الفئة</label>
            <select
              value={newExpense.category}
              onChange={(e) => setNewExpense({...newExpense, category: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {expenseCategories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
        
        <button
          onClick={addExpense}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
        >
          إضافة المصروف
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-red-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-red-800 mb-2">إجمالي المصروفات</h3>
          <p className="text-3xl font-bold text-red-600">
            ج.م {getTotalExpenses().toFixed(2)}
          </p>
        </div>
        
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">عدد المصروفات</h3>
          <p className="text-3xl font-bold text-blue-600">{expenses.length}</p>
        </div>
        
        <div className="bg-yellow-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">متوسط المصروف</h3>
          <p className="text-3xl font-bold text-yellow-600">
            ج.م {expenses.length > 0 ? (getTotalExpenses() / expenses.length).toFixed(2) : '0.00'}
          </p>
        </div>
      </div>

      {/* Expenses by Category */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">المصروفات حسب الفئة</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(getExpensesByCategory()).map(([category, amount]) => (
            <div key={category} className="text-center p-4 border rounded">
              <h4 className="font-medium text-gray-700">{category}</h4>
              <p className="text-xl font-bold text-blue-600">ج.م {amount.toFixed(2)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Expenses List */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">المصروفات</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">الوصف</th>
                <th className="border border-gray-300 p-2">المبلغ</th>
                <th className="border border-gray-300 p-2">الفئة</th>
                <th className="border border-gray-300 p-2">التاريخ</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td className="border border-gray-300 p-2">{expense.description}</td>
                  <td className="border border-gray-300 p-2">
                    <span className="font-semibold text-red-600">
                      ج.م {expense.amount.toFixed(2)}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      expense.category === 'خامات' ? 'bg-blue-100 text-blue-800' :
                      expense.category === 'رواتب' ? 'bg-green-100 text-green-800' :
                      expense.category === 'كهرباء' ? 'bg-yellow-100 text-yellow-800' :
                      expense.category === 'صيانة' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {expense.category}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    {new Date(expense.date).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="border border-gray-300 p-2">
                    <button 
                      onClick={() => deleteExpense(expense.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600">
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {expenses.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              لا توجد مصروفات مسجلة
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Revenue Component
const Revenue = () => {
  const [revenueData, setRevenueData] = useState({
    total_revenue: 0,
    total_expenses: 0,
    material_cost: 0,
    profit: 0
  });
  const [period, setPeriod] = useState('daily');

  useEffect(() => {
    fetchRevenueData();
  }, [period]);

  const fetchRevenueData = async () => {
    try {
      const response = await axios.get(`${API}/reports/revenue?period=${period}`);
      setRevenueData(response.data);
    } catch (error) {
      console.error('Error fetching revenue data:', error);
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">الإيرادات</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={fetchRevenueData}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select 
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2">
            <option value="daily">اليوم</option>
            <option value="weekly">الأسبوع</option>
            <option value="monthly">الشهر</option>
            <option value="yearly">السنة</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Revenue Cards */}
        <div className="bg-green-50 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-green-800 text-center mb-2">إجمالي الإيرادات</h3>
          <p className="text-3xl font-bold text-green-600 text-center">
            ج.م {revenueData.total_revenue?.toFixed(2) || '0.00'}
          </p>
        </div>
        
        <div className="bg-red-50 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-red-800 text-center mb-2">إجمالي المصروفات</h3>
          <p className="text-3xl font-bold text-red-600 text-center">
            ج.م {revenueData.total_expenses?.toFixed(2) || '0.00'}
          </p>
        </div>
        
        <div className="bg-yellow-50 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-yellow-800 text-center mb-2">تكلفة الخامات</h3>
          <p className="text-3xl font-bold text-yellow-600 text-center">
            ج.م {revenueData.material_cost?.toFixed(2) || '0.00'}
          </p>
        </div>
        
        <div className="bg-blue-50 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-blue-800 text-center mb-2">صافي الربح</h3>
          <p className={`text-3xl font-bold text-center ${
            (revenueData.profit || 0) >= 0 ? 'text-blue-600' : 'text-red-600'
          }`}>
            ج.م {revenueData.profit?.toFixed(2) || '0.00'}
          </p>
        </div>
      </div>

      {/* Summary Table */}
      <div className="bg-white p-6 rounded-lg shadow-md mt-6">
        <h3 className="text-lg font-semibold mb-4">تقرير الإيرادات - {
          period === 'daily' ? 'يومي' :
          period === 'weekly' ? 'أسبوعي' :
          period === 'monthly' ? 'شهري' : 'سنوي'
        }</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-3">البيان</th>
                <th className="border border-gray-300 p-3">المبلغ (ج.م)</th>
                <th className="border border-gray-300 p-3">النسبة المئوية</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border border-gray-300 p-3 font-semibold">إجمالي الإيرادات</td>
                <td className="border border-gray-300 p-3 text-green-600 font-bold">
                  {revenueData.total_revenue?.toFixed(2) || '0.00'}
                </td>
                <td className="border border-gray-300 p-3">100%</td>
              </tr>
              <tr>
                <td className="border border-gray-300 p-3">تكلفة الخامات</td>
                <td className="border border-gray-300 p-3 text-yellow-600 font-semibold">
                  -{revenueData.material_cost?.toFixed(2) || '0.00'}
                </td>
                <td className="border border-gray-300 p-3">
                  {revenueData.total_revenue > 0 
                    ? ((revenueData.material_cost / revenueData.total_revenue) * 100).toFixed(1) 
                    : '0.0'}%
                </td>
              </tr>
              <tr>
                <td className="border border-gray-300 p-3">مصروفات أخرى</td>
                <td className="border border-gray-300 p-3 text-red-600 font-semibold">
                  -{((revenueData.total_expenses || 0) - (revenueData.material_cost || 0)).toFixed(2)}
                </td>
                <td className="border border-gray-300 p-3">
                  {revenueData.total_revenue > 0 
                    ? (((revenueData.total_expenses - revenueData.material_cost) / revenueData.total_revenue) * 100).toFixed(1) 
                    : '0.0'}%
                </td>
              </tr>
              <tr className="bg-blue-50">
                <td className="border border-gray-300 p-3 font-bold">صافي الربح</td>
                <td className={`border border-gray-300 p-3 font-bold ${
                  (revenueData.profit || 0) >= 0 ? 'text-blue-600' : 'text-red-600'
                }`}>
                  {revenueData.profit?.toFixed(2) || '0.00'}
                </td>
                <td className="border border-gray-300 p-3 font-bold">
                  {revenueData.total_revenue > 0 
                    ? ((revenueData.profit / revenueData.total_revenue) * 100).toFixed(1) 
                    : '0.0'}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="bg-white p-6 rounded-lg shadow-md mt-6">
        <h3 className="text-lg font-semibold mb-4">مؤشرات الأداء</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 border rounded">
            <h4 className="font-medium text-gray-700 mb-2">هامش الربح</h4>
            <p className={`text-2xl font-bold ${
              (revenueData.profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {revenueData.total_revenue > 0 
                ? ((revenueData.profit / revenueData.total_revenue) * 100).toFixed(1) 
                : '0.0'}%
            </p>
          </div>
          
          <div className="text-center p-4 border rounded">
            <h4 className="font-medium text-gray-700 mb-2">نسبة تكلفة الخامات</h4>
            <p className="text-2xl font-bold text-yellow-600">
              {revenueData.total_revenue > 0 
                ? ((revenueData.material_cost / revenueData.total_revenue) * 100).toFixed(1) 
                : '0.0'}%
            </p>
          </div>
          
          <div className="text-center p-4 border rounded">
            <h4 className="font-medium text-gray-700 mb-2">نسبة المصروفات الإجمالية</h4>
            <p className="text-2xl font-bold text-red-600">
              {revenueData.total_revenue > 0 
                ? ((revenueData.total_expenses / revenueData.total_revenue) * 100).toFixed(1) 
                : '0.0'}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Invoices Component
const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [filterStatus, setFilterStatus] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchInvoices();
    fetchCustomers();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const deleteInvoice = async (invoiceId) => {
    if (!confirm('هل أنت متأكد من حذف هذه الفاتورة؟')) return;

    try {
      await axios.delete(`${API}/invoices/${invoiceId}`);
      fetchInvoices();
      alert('تم حذف الفاتورة بنجاح');
    } catch (error) {
      console.error('Error deleting invoice:', error);
      alert('حدث خطأ في حذف الفاتورة');
    }
  };

  const updateInvoiceStatus = async (invoiceId, newStatus) => {
    try {
      await axios.put(`${API}/invoices/${invoiceId}/status`, newStatus, {
        headers: { 'Content-Type': 'application/json' }
      });
      fetchInvoices();
      alert('تم تحديث حالة الفاتورة');
    } catch (error) {
      console.error('Error updating invoice status:', error);
      alert('حدث خطأ في تحديث حالة الفاتورة');
    }
  };

  const printInvoice = (invoice) => {
    const printContent = `
      <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h1>ماستر سيل</h1>
          <p>الحرفيان شارع السوبر جيت - 01020630677</p>
        </div>
        <div style="margin-bottom: 20px;">
          <strong>رقم الفاتورة:</strong> ${invoice.invoice_number}<br>
          <strong>العميل:</strong> ${invoice.customer_name}<br>
          <strong>التاريخ:</strong> ${new Date(invoice.date).toLocaleDateString('ar-EG')}<br>
          <strong>طريقة الدفع:</strong> ${invoice.payment_method}
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #f0f0f0;">
              <th style="border: 1px solid #ddd; padding: 8px;">المنتج</th>
              <th style="border: 1px solid #ddd; padding: 8px;">الكمية</th>
              <th style="border: 1px solid #ddd; padding: 8px;">السعر</th>
              <th style="border: 1px solid #ddd; padding: 8px;">المجموع</th>
            </tr>
          </thead>
          <tbody>
            ${invoice.items.map(item => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">
                  ${item.seal_type} - ${item.material_type}<br>
                  ${item.inner_diameter} × ${item.outer_diameter} × ${item.height}
                </td>
                <td style="border: 1px solid #ddd; padding: 8px;">${item.quantity}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">ج.م ${item.unit_price}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">ج.م ${item.total_price}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div style="text-align: left;">
          <strong>الإجمالي: ج.م ${invoice.total_amount}</strong>
        </div>
      </div>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesStatus = filterStatus === '' || invoice.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.customer_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">الفواتير</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={fetchInvoices}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">البحث</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="رقم الفاتورة أو اسم العميل"
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">فلترة حسب الحالة</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="">جميع الحالات</option>
              <option value="مدفوعة">مدفوعة</option>
              <option value="غير مدفوعة">غير مدفوعة</option>
              <option value="مدفوعة جزئياً">مدفوعة جزئياً</option>
              <option value="انتظار">انتظار</option>
              <option value="تم التنفيذ">تم التنفيذ</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => { setSearchTerm(''); setFilterStatus(''); }}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              مسح الفلاتر
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg text-center">
          <h3 className="font-semibold text-blue-800">إجمالي الفواتير</h3>
          <p className="text-2xl font-bold text-blue-600">{invoices.length}</p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg text-center">
          <h3 className="font-semibold text-green-800">المدفوعة</h3>
          <p className="text-2xl font-bold text-green-600">
            {invoices.filter(inv => inv.status === 'مدفوعة').length}
          </p>
        </div>
        
        <div className="bg-red-50 p-4 rounded-lg text-center">
          <h3 className="font-semibold text-red-800">غير المدفوعة</h3>
          <p className="text-2xl font-bold text-red-600">
            {invoices.filter(inv => inv.status === 'غير مدفوعة').length}
          </p>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg text-center">
          <h3 className="font-semibold text-yellow-800">الإجمالي</h3>
          <p className="text-2xl font-bold text-yellow-600">
            ج.م {invoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">جميع الفواتير</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">رقم الفاتورة</th>
                <th className="border border-gray-300 p-2">العميل</th>
                <th className="border border-gray-300 p-2">التاريخ</th>
                <th className="border border-gray-300 p-2">طريقة الدفع</th>
                <th className="border border-gray-300 p-2">الإجمالي</th>
                <th className="border border-gray-300 p-2">الحالة</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {filteredInvoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="border border-gray-300 p-2 font-semibold">
                    {invoice.invoice_number}
                  </td>
                  <td className="border border-gray-300 p-2">{invoice.customer_name}</td>
                  <td className="border border-gray-300 p-2">
                    {new Date(invoice.date).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="border border-gray-300 p-2">{invoice.payment_method}</td>
                  <td className="border border-gray-300 p-2 font-semibold">
                    ج.م {invoice.total_amount?.toFixed(2) || '0.00'}
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className={`px-2 py-1 rounded text-sm cursor-pointer ${
                      invoice.status === 'مدفوعة' ? 'bg-green-100 text-green-800' :
                      invoice.status === 'غير مدفوعة' ? 'bg-red-100 text-red-800' :
                      invoice.status === 'مدفوعة جزئياً' ? 'bg-yellow-100 text-yellow-800' :
                      invoice.status === 'انتظار' ? 'bg-blue-100 text-blue-800' :
                      invoice.status === 'تم التنفيذ' ? 'bg-green-100 text-green-800' :
                      invoice.status === 'تم التصنيع' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {invoice.status}
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button
                        onClick={() => printInvoice(invoice)}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                      >
                        طباعة
                      </button>
                      <button
                        onClick={() => deleteInvoice(invoice.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                      >
                        حذف
                      </button>
                      {invoice.status === 'انتظار' && (
                        <button
                          onClick={() => updateInvoiceStatus(invoice.id, 'تم التنفيذ')}
                          className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                        >
                          تم التنفيذ
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredInvoices.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              لا توجد فواتير تطابق معايير البحث
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Work Orders Component
const WorkOrders = () => {
  const [workOrders, setWorkOrders] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoices, setSelectedInvoices] = useState([]);
  const [newWorkOrder, setNewWorkOrder] = useState({
    title: '',
    description: '',
    priority: 'عادي'
  });

  useEffect(() => {
    fetchWorkOrders();
    fetchInvoices();
  }, []);

  const fetchWorkOrders = async () => {
    try {
      const response = await axios.get(`${API}/work-orders`);
      setWorkOrders(response.data);
    } catch (error) {
      console.error('Error fetching work orders:', error);
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  const toggleInvoiceSelection = (invoiceId) => {
    setSelectedInvoices(prev => 
      prev.includes(invoiceId) 
        ? prev.filter(id => id !== invoiceId)
        : [...prev, invoiceId]
    );
  };

  const createWorkOrderFromMultipleInvoices = async () => {
    if (selectedInvoices.length === 0) {
      alert('الرجاء اختيار فاتورة واحدة على الأقل');
      return;
    }

    if (!newWorkOrder.title.trim()) {
      alert('الرجاء إدخال عنوان أمر الشغل');
      return;
    }

    try {
      // Get selected invoices data
      const selectedInvoicesData = invoices.filter(inv => selectedInvoices.includes(inv.id));
      
      // Create work order with multiple invoices
      const workOrderData = {
        title: newWorkOrder.title,
        description: newWorkOrder.description,
        priority: newWorkOrder.priority,
        invoices: selectedInvoicesData,
        total_amount: selectedInvoicesData.reduce((sum, inv) => sum + (inv.total_amount || 0), 0),
        total_items: selectedInvoicesData.reduce((sum, inv) => sum + (inv.items?.length || 0), 0)
      };

      const response = await axios.post(`${API}/work-orders/multiple`, workOrderData);
      
      if (response.data) {
        alert('تم إنشاء أمر الشغل بنجاح');
        
        // Reset form
        setSelectedInvoices([]);
        setNewWorkOrder({
          title: '',
          description: '',
          priority: 'عادي'
        });
        
        fetchWorkOrders();
      }
    } catch (error) {
      console.error('Error creating work order:', error);
      alert('حدث خطأ في إنشاء أمر الشغل');
    }
  };

  const getInvoiceDetails = (invoiceId) => {
    return invoices.find(inv => inv.id === invoiceId);
  };

  const getAvailableInvoices = () => {
    // Show invoices that are "تم التنفيذ" or "انتظار"
    return invoices.filter(invoice => 
      invoice.status === 'تم التنفيذ' || invoice.status === 'انتظار'
    );
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">أمر شغل</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button 
            onClick={() => { fetchWorkOrders(); fetchInvoices(); }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Create Work Order from Multiple Invoices */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">إنشاء أمر شغل جديد</h3>
        
        {/* Work Order Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">عنوان أمر الشغل *</label>
            <input
              type="text"
              value={newWorkOrder.title}
              onChange={(e) => setNewWorkOrder({...newWorkOrder, title: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="مثال: أمر شغل رقم 1 - يناير 2025"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الأولوية</label>
            <select
              value={newWorkOrder.priority}
              onChange={(e) => setNewWorkOrder({...newWorkOrder, priority: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="عادي">عادي</option>
              <option value="مهم">مهم</option>
              <option value="طارئ">طارئ</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الفواتير المختارة</label>
            <div className="p-2 bg-gray-100 rounded">
              {selectedInvoices.length} فاتورة محددة
            </div>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">وصف أمر الشغل</label>
          <textarea
            value={newWorkOrder.description}
            onChange={(e) => setNewWorkOrder({...newWorkOrder, description: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded h-20"
            placeholder="وصف إضافي (اختياري)"
          />
        </div>
        
        <h4 className="font-medium mb-2">اختيار الفواتير:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4 max-h-60 overflow-y-auto border rounded p-4">
          {getAvailableInvoices().map(invoice => (
            <div 
              key={invoice.id} 
              className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                selectedInvoices.includes(invoice.id) 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => toggleInvoiceSelection(invoice.id)}
            >
              <div className="flex items-center mb-2">
                <input
                  type="checkbox"
                  checked={selectedInvoices.includes(invoice.id)}
                  onChange={() => {}}
                  className="ml-2"
                />
                <h5 className="font-semibold">{invoice.invoice_number}</h5>
              </div>
              <p className="text-sm text-gray-600">العميل: {invoice.customer_name}</p>
              <p className="text-sm text-gray-600">
                التاريخ: {new Date(invoice.date).toLocaleDateString('ar-EG')}
              </p>
              <p className="text-sm font-medium">
                المبلغ: ج.م {invoice.total_amount?.toFixed(2) || '0.00'}
              </p>
              <p className="text-sm">
                المنتجات: {invoice.items?.length || 0} صنف
              </p>
              <span className={`inline-block px-2 py-1 rounded text-xs mt-1 ${
                invoice.status === 'تم التنفيذ' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {invoice.status}
              </span>
            </div>
          ))}
        </div>
        
        {getAvailableInvoices().length === 0 && (
          <div className="text-center py-8 text-gray-500">
            لا توجد فواتير متاحة لإنشاء أمر شغل
          </div>
        )}
        
        {selectedInvoices.length > 0 && (
          <div className="mb-4 p-3 bg-blue-100 rounded">
            <h5 className="font-semibold text-blue-800">ملخص أمر الشغل:</h5>
            <p className="text-blue-700">
              إجمالي الفواتير: {selectedInvoices.length} فاتورة
            </p>
            <p className="text-blue-700">
              إجمالي المبلغ: ج.م {invoices
                .filter(inv => selectedInvoices.includes(inv.id))
                .reduce((sum, inv) => sum + (inv.total_amount || 0), 0)
                .toFixed(2)}
            </p>
            <p className="text-blue-700">
              إجمالي المنتجات: {invoices
                .filter(inv => selectedInvoices.includes(inv.id))
                .reduce((sum, inv) => sum + (inv.items?.length || 0), 0)} صنف
            </p>
          </div>
        )}
        
        <button
          onClick={createWorkOrderFromMultipleInvoices}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
          disabled={selectedInvoices.length === 0}
        >
          إنشاء أمر الشغل ({selectedInvoices.length} فاتورة)
        </button>
      </div>

      {/* Work Orders List */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">أوامر الشغل</h3>
        
        {workOrders.map(workOrder => {
          // Handle both single invoice and multiple invoices work orders
          const workOrderInvoices = workOrder.invoices || (workOrder.invoice_id ? [getInvoiceDetails(workOrder.invoice_id)] : []);
          
          return (
            <div key={workOrder.id} className="border rounded-lg p-4 mb-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="font-semibold text-lg">
                    {workOrder.title || `أمر شغل #${workOrder.id.slice(-8)}`}
                  </h4>
                  <p><strong>الأولوية:</strong> 
                    <span className={`mr-2 px-2 py-1 rounded text-sm ${
                      workOrder.priority === 'طارئ' ? 'bg-red-100 text-red-800' :
                      workOrder.priority === 'مهم' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {workOrder.priority || 'عادي'}
                    </span>
                  </p>
                  <p><strong>تاريخ الإنشاء:</strong> {new Date(workOrder.created_at).toLocaleDateString('ar-EG')}</p>
                  <p><strong>عدد الفواتير:</strong> {workOrderInvoices.filter(inv => inv).length}</p>
                </div>
                
                <div>
                  <p><strong>الحالة:</strong> 
                    <span className="mr-2 px-2 py-1 rounded text-sm bg-blue-100 text-blue-800">
                      {workOrder.status || 'جديد'}
                    </span>
                  </p>
                  <p><strong>إجمالي المبلغ:</strong> 
                    ج.م {workOrder.total_amount?.toFixed(2) || 
                    workOrderInvoices.reduce((sum, inv) => sum + (inv?.total_amount || 0), 0).toFixed(2)}
                  </p>
                  {workOrder.description && (
                    <p><strong>الوصف:</strong> {workOrder.description}</p>
                  )}
                </div>
              </div>
              
              {/* Work Order Invoices */}
              <div className="mb-4">
                <h5 className="font-medium mb-2">الفواتير المدرجة:</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {workOrderInvoices.filter(invoice => invoice).map((invoice, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded border">
                      <p><strong>رقم الفاتورة:</strong> {invoice.invoice_number}</p>
                      <p><strong>العميل:</strong> {invoice.customer_name}</p>
                      <p><strong>المبلغ:</strong> ج.م {invoice.total_amount?.toFixed(2) || '0.00'}</p>
                      <p><strong>المنتجات:</strong> {invoice.items?.length || 0} صنف</p>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Work Order Items Details */}
              <div className="overflow-x-auto mb-4">
                <h5 className="font-medium mb-2">تفاصيل المنتجات:</h5>
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 p-2">رقم الفاتورة</th>
                      <th className="border border-gray-300 p-2">نوع السيل</th>
                      <th className="border border-gray-300 p-2">نوع الخامة</th>
                      <th className="border border-gray-300 p-2">المقاس</th>
                      <th className="border border-gray-300 p-2">الكمية</th>
                      <th className="border border-gray-300 p-2">الخامة المستخدمة</th>
                      <th className="border border-gray-300 p-2">كود الوحدة</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workOrderInvoices.filter(invoice => invoice).map(invoice => 
                      invoice.items?.map((item, itemIndex) => (
                        <tr key={`${invoice.id}-${itemIndex}`}>
                          <td className="border border-gray-300 p-2">{invoice.invoice_number}</td>
                          <td className="border border-gray-300 p-2">{item.seal_type}</td>
                          <td className="border border-gray-300 p-2">{item.material_type}</td>
                          <td className="border border-gray-300 p-2">
                            {item.inner_diameter} × {item.outer_diameter} × {item.height}
                          </td>
                          <td className="border border-gray-300 p-2">{item.quantity}</td>
                          <td className="border border-gray-300 p-2">
                            <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                              {item.material_type}
                            </span>
                          </td>
                          <td className="border border-gray-300 p-2">
                            <span className="font-mono text-sm">
                              {item.material_used || 'غير محدد'}
                            </span>
                          </td>
                        </tr>
                      )) || []
                    )}
                  </tbody>
                </table>
              </div>
              
              {/* Work Order Actions */}
              <div className="flex space-x-4 space-x-reverse">
                <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                  طباعة أمر الشغل
                </button>
                <button className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">
                  تعديل الحالة
                </button>
                <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                  حذف
                </button>
              </div>
            </div>
          );
        })}
        
        {workOrders.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            لا توجد أوامر شغل
          </div>
        )}
      </div>
    </div>
  );
};

// Users Management Component  
const Users = () => {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    role: 'user'
  });
  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({
    username: '',
    password: '',
    role: 'user'
  });
  const [companyInfo, setCompanyInfo] = useState({
    name: 'ماستر سيل',
    address: 'الحرفيان شارع السوبر جيت',
    phone: '01020630677'
  });
  const [editingCompany, setEditingCompany] = useState(false);
  const [selectedUserPermissions, setSelectedUserPermissions] = useState(null);

  const allPermissions = [
    { key: 'dashboard', label: 'لوحة التحكم' },
    { key: 'sales', label: 'المبيعات' },
    { key: 'inventory', label: 'المخزون' },
    { key: 'deferred', label: 'الآجل' },
    { key: 'expenses', label: 'المصروفات' },
    { key: 'revenue', label: 'الإيرادات' },
    { key: 'invoices', label: 'الفواتير' },
    { key: 'work-orders', label: 'أمر شغل' },
    { key: 'users', label: 'إدارة المستخدمين' }
  ];

  useEffect(() => {
    // Since users are predefined, we'll show them statically
    setUsers([
      { 
        id: '1', 
        username: 'Elsawy', 
        role: 'admin', 
        created_at: new Date().toISOString(),
        permissions: allPermissions.map(p => p.key)
      },
      { 
        id: '2', 
        username: 'Root', 
        role: 'user', 
        created_at: new Date().toISOString(),
        permissions: ['dashboard', 'sales', 'inventory', 'deferred', 'expenses', 'work-orders']
      }
    ]);
  }, []);

  const addUser = async () => {
    if (!newUser.username || !newUser.password) {
      alert('الرجاء إدخال اسم المستخدم وكلمة المرور');
      return;
    }

    // Check if username already exists
    if (users.some(user => user.username === newUser.username)) {
      alert('اسم المستخدم موجود بالفعل');
      return;
    }

    // Default permissions based on role
    const defaultPermissions = newUser.role === 'admin' 
      ? allPermissions.map(p => p.key)
      : ['dashboard', 'sales', 'inventory', 'deferred', 'expenses', 'work-orders'];

    const user = {
      id: Date.now().toString(),
      username: newUser.username,
      role: newUser.role,
      permissions: defaultPermissions,
      created_at: new Date().toISOString()
    };

    setUsers([...users, user]);
    setNewUser({ username: '', password: '', role: 'user' });
    alert('تم إضافة المستخدم بنجاح');
  };

  const startEdit = (user) => {
    setEditingUser(user.id);
    setEditForm({
      username: user.username,
      password: '',
      role: user.role
    });
  };

  const cancelEdit = () => {
    setEditingUser(null);
    setEditForm({ username: '', password: '', role: 'user' });
  };

  const saveEdit = () => {
    if (!editForm.username) {
      alert('الرجاء إدخال اسم المستخدم');
      return;
    }

    // Check if username already exists (excluding current user)
    if (users.some(user => user.username === editForm.username && user.id !== editingUser)) {
      alert('اسم المستخدم موجود بالفعل');
      return;
    }

    setUsers(users.map(user => 
      user.id === editingUser 
        ? { ...user, username: editForm.username, role: editForm.role }
        : user
    ));

    setEditingUser(null);
    setEditForm({ username: '', password: '', role: 'user' });
    alert('تم تحديث المستخدم بنجاح');
  };

  const deleteUser = (userId) => {
    if (userId === '1' || userId === '2') {
      alert('لا يمكن حذف المستخدمين الأساسيين');
      return;
    }

    if (!confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return;

    setUsers(users.filter(user => user.id !== userId));
    alert('تم حذف المستخدم بنجاح');
  };

  const resetPassword = (userId) => {
    const newPassword = prompt('أدخل كلمة المرور الجديدة:');
    if (newPassword && newPassword.trim()) {
      alert(`تم تحديث كلمة المرور للمستخدم بنجاح`);
    }
  };

  const openPermissions = (user) => {
    setSelectedUserPermissions({
      ...user,
      tempPermissions: [...(user.permissions || [])]
    });
  };

  const togglePermission = (permissionKey) => {
    setSelectedUserPermissions(prev => {
      const newPermissions = prev.tempPermissions.includes(permissionKey)
        ? prev.tempPermissions.filter(p => p !== permissionKey)
        : [...prev.tempPermissions, permissionKey];
      
      return { ...prev, tempPermissions: newPermissions };
    });
  };

  const savePermissions = () => {
    setUsers(users.map(user => 
      user.id === selectedUserPermissions.id 
        ? { ...user, permissions: selectedUserPermissions.tempPermissions }
        : user
    ));
    setSelectedUserPermissions(null);
    alert('تم تحديث الصلاحيات بنجاح');
  };

  const saveCompanyInfo = () => {
    setEditingCompany(false);
    alert('تم تحديث بيانات الشركة بنجاح');
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">إدارة المستخدمين</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            حذف الكل
          </button>
          <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            طباعة تقرير
          </button>
        </div>
      </div>

      {/* Company Information */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">بيانات الشركة</h3>
        
        {editingCompany ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">اسم الشركة</label>
              <input
                type="text"
                value={companyInfo.name}
                onChange={(e) => setCompanyInfo({...companyInfo, name: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">العنوان</label>
              <input
                type="text"
                value={companyInfo.address}
                onChange={(e) => setCompanyInfo({...companyInfo, address: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">التليفون</label>
              <input
                type="text"
                value={companyInfo.phone}
                onChange={(e) => setCompanyInfo({...companyInfo, phone: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">اسم الشركة</label>
              <p className="p-2 bg-gray-100 rounded">{companyInfo.name}</p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">العنوان</label>
              <p className="p-2 bg-gray-100 rounded">{companyInfo.address}</p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">التليفون</label>
              <p className="p-2 bg-gray-100 rounded">{companyInfo.phone}</p>
            </div>
          </div>
        )}
        
        <div className="flex space-x-4 space-x-reverse">
          {editingCompany ? (
            <>
              <button
                onClick={saveCompanyInfo}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                حفظ
              </button>
              <button
                onClick={() => setEditingCompany(false)}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
            </>
          ) : (
            <button
              onClick={() => setEditingCompany(true)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              تعديل بيانات الشركة
            </button>
          )}
        </div>
      </div>

      {/* Add New User */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">إضافة مستخدم جديد</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">اسم المستخدم</label>
            <input
              type="text"
              value={newUser.username}
              onChange={(e) => setNewUser({...newUser, username: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="اسم المستخدم"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">كلمة المرور</label>
            <input
              type="password"
              value={newUser.password}
              onChange={(e) => setNewUser({...newUser, password: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="كلمة المرور"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">الصلاحية</label>
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({...newUser, role: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="user">مستخدم عادي</option>
              <option value="admin">مدير</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={addUser}
          className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
        >
          إضافة المستخدم
        </button>
      </div>

      {/* Users Table */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">المستخدمين</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">اسم المستخدم</th>
                <th className="border border-gray-300 p-2">الصلاحية</th>
                <th className="border border-gray-300 p-2">عدد الصلاحيات</th>
                <th className="border border-gray-300 p-2">تاريخ الإنشاء</th>
                <th className="border border-gray-300 p-2">الحالة</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="border border-gray-300 p-2">
                    {editingUser === user.id ? (
                      <input
                        type="text"
                        value={editForm.username}
                        onChange={(e) => setEditForm({...editForm, username: e.target.value})}
                        className="w-full p-1 border border-gray-300 rounded"
                      />
                    ) : (
                      <span className="font-semibold">{user.username}</span>
                    )}
                  </td>
                  <td className="border border-gray-300 p-2">
                    {editingUser === user.id ? (
                      <select
                        value={editForm.role}
                        onChange={(e) => setEditForm({...editForm, role: e.target.value})}
                        className="w-full p-1 border border-gray-300 rounded"
                      >
                        <option value="user">مستخدم عادي</option>
                        <option value="admin">مدير</option>
                      </select>
                    ) : (
                      <span className={`px-2 py-1 rounded text-sm ${
                        user.role === 'admin' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {user.role === 'admin' ? 'مدير' : 'مستخدم عادي'}
                      </span>
                    )}
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className="bg-gray-100 px-2 py-1 rounded text-sm">
                      {user.permissions?.length || 0} صلاحية
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    {new Date(user.created_at).toLocaleDateString('ar-EG')}
                  </td>
                  <td className="border border-gray-300 p-2">
                    <span className="px-2 py-1 rounded text-sm bg-green-100 text-green-800">
                      نشط
                    </span>
                  </td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse flex-wrap">
                      {editingUser === user.id ? (
                        <>
                          <button 
                            onClick={saveEdit}
                            className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600 mb-1">
                            حفظ
                          </button>
                          <button 
                            onClick={cancelEdit}
                            className="bg-gray-500 text-white px-2 py-1 rounded text-sm hover:bg-gray-600 mb-1">
                            إلغاء
                          </button>
                        </>
                      ) : (
                        <>
                          <button 
                            onClick={() => startEdit(user)}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600 mb-1">
                            تعديل
                          </button>
                          <button 
                            onClick={() => openPermissions(user)}
                            className="bg-purple-500 text-white px-2 py-1 rounded text-sm hover:bg-purple-600 mb-1">
                            الصلاحيات
                          </button>
                          <button 
                            onClick={() => resetPassword(user.id)}
                            className="bg-yellow-500 text-white px-2 py-1 rounded text-sm hover:bg-yellow-600 mb-1">
                            كلمة المرور
                          </button>
                          {(user.id !== '1' && user.id !== '2') && (
                            <button 
                              onClick={() => deleteUser(user.id)}
                              className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600 mb-1">
                              حذف
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Permissions Modal */}
      {selectedUserPermissions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4">
              صلاحيات المستخدم: {selectedUserPermissions.username}
            </h3>
            
            <div className="space-y-2 mb-4">
              {allPermissions.map(permission => (
                <label key={permission.key} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedUserPermissions.tempPermissions.includes(permission.key)}
                    onChange={() => togglePermission(permission.key)}
                    className="ml-2"
                  />
                  <span>{permission.label}</span>
                </label>
              ))}
            </div>
            
            <div className="flex space-x-4 space-x-reverse">
              <button
                onClick={savePermissions}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                حفظ
              </button>
              <button
                onClick={() => setSelectedUserPermissions(null)}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const { user } = useAuth();

  if (!user) return <Login />;

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'sales': return <Sales />;
      case 'inventory': return <Inventory />;
      case 'deferred': return <Deferred />;
      case 'expenses': return <Expenses />;
      case 'revenue': return <Revenue />;
      case 'invoices': return <Invoices />;
      case 'work-orders': return <WorkOrders />;
      case 'users': return <Users />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      <main>
        {renderPage()}
      </main>
    </div>
  );
};

// Root App with AuthProvider
const AppWithAuth = () => (
  <AuthProvider>
    <App />
  </AuthProvider>
);

export default AppWithAuth;