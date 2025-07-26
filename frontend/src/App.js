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
          <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
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
      total_price: parseFloat(currentItem.unit_price) * parseInt(currentItem.quantity)
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
                    className={`p-3 border rounded ${material.low_stock ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'}`}
                  >
                    <p><strong>النوع:</strong> {material.material_type}</p>
                    <p><strong>الكود:</strong> {material.unit_code}</p>
                    <p><strong>المقاس:</strong> {material.inner_diameter} × {material.outer_diameter} × {material.height}</p>
                    {material.warning && <p className="text-red-600 text-sm">{material.warning}</p>}
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
                  <div key={index} className="p-3 border border-blue-300 bg-blue-50 rounded">
                    <p><strong>النوع:</strong> {product.seal_type} - {product.material_type}</p>
                    <p><strong>المقاس:</strong> {product.inner_diameter} × {product.outer_diameter} × {product.height}</p>
                    <p><strong>الكمية:</strong> {product.quantity}</p>
                  </div>
                ))}
              </div>
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
          
          <button className="w-full bg-green-500 text-white p-3 rounded hover:bg-green-600 mt-4 text-lg font-semibold">
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
          <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
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
          <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
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

const Expenses = () => (
  <div className="p-6" dir="rtl">
    <h2 className="text-2xl font-bold text-blue-600 mb-6">المصروفات</h2>
    <div className="bg-white p-6 rounded-lg shadow-md">
      <p>صفحة المصروفات قيد التطوير...</p>
    </div>
  </div>
);

const Revenue = () => (
  <div className="p-6" dir="rtl">
    <h2 className="text-2xl font-bold text-blue-600 mb-6">الإيرادات</h2>
    <div className="bg-white p-6 rounded-lg shadow-md">
      <p>صفحة الإيرادات قيد التطوير...</p>
    </div>
  </div>
);

const Invoices = () => (
  <div className="p-6" dir="rtl">
    <h2 className="text-2xl font-bold text-blue-600 mb-6">الفواتير</h2>
    <div className="bg-white p-6 rounded-lg shadow-md">
      <p>صفحة الفواتير قيد التطوير...</p>
    </div>
  </div>
);

const WorkOrders = () => (
  <div className="p-6" dir="rtl">
    <h2 className="text-2xl font-bold text-blue-600 mb-6">أمر شغل</h2>
    <div className="bg-white p-6 rounded-lg shadow-md">
      <p>صفحة أمر شغل قيد التطوير...</p>
    </div>
  </div>
);

const Users = () => (
  <div className="p-6" dir="rtl">
    <h2 className="text-2xl font-bold text-blue-600 mb-6">إدارة المستخدمين</h2>
    <div className="bg-white p-6 rounded-lg shadow-md">
      <p>صفحة إدارة المستخدمين قيد التطوير...</p>
    </div>
  </div>
);

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