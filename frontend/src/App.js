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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center p-4" dir="rtl">
      <div className="max-w-md w-full">
        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-blue-100">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mb-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_oilseal-mgmt/artifacts/42i3e7yn_WhatsApp%20Image%202025-07-31%20at%2015.14.10_e8c55120.jpg" 
                alt="Master Seal Logo" 
                className="h-16 w-16 mx-auto rounded-full shadow-lg border-4 border-blue-100"
              />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">ماستر سيل</h1>
            <p className="text-gray-500 mt-2">نظام إدارة الشركة المتكامل</p>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-400 to-blue-600 mx-auto mt-3 rounded-full"></div>
          </div>
          
          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                👤 اسم المستخدم
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-3 focus:ring-blue-200 focus:border-blue-400 transition-all duration-200 bg-gray-50 hover:bg-white"
                placeholder="ادخل اسم المستخدم"
                required
              />
            </div>
            
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🔒 كلمة المرور
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-3 focus:ring-blue-200 focus:border-blue-400 transition-all duration-200 bg-gray-50 hover:bg-white"
                placeholder="ادخل كلمة المرور"
                required
              />
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm text-center animate-pulse">
                ⚠️ {error}
              </div>
            )}
            
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-blue-800 text-white py-3 px-6 rounded-xl hover:from-blue-700 hover:to-blue-900 focus:outline-none focus:ring-3 focus:ring-blue-300 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              🚀 دخول
            </button>
          </form>
          
          {/* Footer */}
          <div className="text-center mt-8 pt-6 border-t border-gray-100">
            <p className="text-xs text-gray-400">الحرفيين - السلام - أمام السوبر جيت</p>
            <p className="text-xs text-gray-500 mt-1 font-medium">📞 01020630677</p>
          </div>
        </div>
        
        {/* Additional Info Card */}
        <div className="mt-6 bg-white/60 backdrop-blur-sm rounded-xl p-4 text-center border border-blue-100/50">
          <p className="text-sm text-gray-600">نظام إدارة متكامل لإدارة المبيعات والمخزون والحسابات</p>
        </div>
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = ({ currentPage, onPageChange }) => {
  const { user, logout } = useAuth();
  
  // Dashboard is only for Elsawy
  const elsawyPages = [
    { key: 'dashboard', label: 'لوحة التحكم', icon: '📊' },
    { key: 'sales', label: 'المبيعات', icon: '💰' },
    { key: 'inventory', label: 'الجرد', icon: '📦' },
    { key: 'stock', label: 'المخزون', icon: '🏪' },
    { key: 'local', label: 'محلي', icon: '🏭' },
    { key: 'deferred', label: 'الآجل', icon: '⏳' },
    { key: 'expenses', label: 'المصروفات', icon: '💸' },
    { key: 'revenue', label: 'الإيرادات', icon: '📈' },
    { key: 'treasury', label: 'الخزينة', icon: '🏦' },
    { key: 'invoices', label: 'الفواتير', icon: '🧾' },
    { key: 'work-orders', label: 'أمر شغل', icon: '⚙️' },
    { key: 'pricing', label: 'التسعير', icon: '💲' },
    { key: 'users', label: 'المستخدمين', icon: '👥' }
  ];
  
  const adminPages = [
    { key: 'sales', label: 'المبيعات', icon: '💰' },
    { key: 'inventory', label: 'الجرد', icon: '📦' },
    { key: 'stock', label: 'المخزون', icon: '🏪' },
    { key: 'local', label: 'محلي', icon: '🏭' },
    { key: 'deferred', label: 'الآجل', icon: '⏳' },
    { key: 'expenses', label: 'المصروفات', icon: '💸' },
    { key: 'revenue', label: 'الإيرادات', icon: '📈' },
    { key: 'treasury', label: 'الخزينة', icon: '🏦' },
    { key: 'invoices', label: 'الفواتير', icon: '🧾' },
    { key: 'work-orders', label: 'أمر شغل', icon: '⚙️' },
    { key: 'pricing', label: 'التسعير', icon: '💲' },
    { key: 'users', label: 'المستخدمين', icon: '👥' }
  ];
  
  const userPages = [
    { key: 'sales', label: 'المبيعات', icon: '💰' },
    { key: 'inventory', label: 'الجرد', icon: '📦' },
    { key: 'stock', label: 'المخزون', icon: '🏪' },
    { key: 'local', label: 'محلي', icon: '🏭' },
    { key: 'deferred', label: 'الآجل', icon: '⏳' },
    { key: 'expenses', label: 'المصروفات', icon: '💸' },
    { key: 'treasury', label: 'الخزينة', icon: '🏦' },
    { key: 'invoices', label: 'الفواتير', icon: '🧾' },
    { key: 'work-orders', label: 'أمر شغل', icon: '⚙️' },
    { key: 'pricing', label: 'التسعير', icon: '💲' }
  ];
  
  // Only Elsawy gets dashboard access
  const pages = user?.username === 'Elsawy' ? elsawyPages : 
               user?.role === 'admin' ? adminPages : userPages;

  return (
    <div className="w-80 bg-gradient-to-b from-blue-900 via-blue-800 to-blue-900 text-white shadow-2xl">
      {/* Header */}
      <div className="p-6 border-b border-blue-700">
        <div className="flex items-center space-x-3 space-x-reverse">
          <img 
            src="https://customer-assets.emergentagent.com/job_oilseal-mgmt/artifacts/42i3e7yn_WhatsApp%20Image%202025-07-31%20at%2015.14.10_e8c55120.jpg" 
            alt="Master Seal Logo" 
            className="h-12 w-12 rounded-lg shadow-lg"
          />
          <div>
            <h1 className="text-xl font-bold text-white">ماستر سيل</h1>
            <p className="text-xs text-blue-200">نظام إدارة متكامل</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 bg-blue-800 border-b border-blue-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">أهلاً وسهلاً</p>
            <p className="text-lg font-bold text-blue-200">{user?.username}</p>
          </div>
          <button
            onClick={logout}
            className="bg-red-500 hover:bg-red-600 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            خروج
          </button>
        </div>
      </div>
      
      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-2">
        {pages.map(page => (
          <button
            key={page.key}
            onClick={() => onPageChange(page.key)}
            className={`w-full flex items-center space-x-3 space-x-reverse p-4 rounded-xl text-right transition-all duration-200 group ${
              currentPage === page.key 
                ? 'bg-white text-blue-900 shadow-lg transform scale-105' 
                : 'hover:bg-blue-700 hover:transform hover:translate-x-2'
            }`}
          >
            <span className="text-2xl">{page.icon}</span>
            <span className="font-medium">{page.label}</span>
            {currentPage === page.key && (
              <div className="mr-auto">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              </div>
            )}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-blue-700 text-center">
        <p className="text-xs text-blue-300">الحرفيين - السلام - أمام السوبر جيت</p>
        <p className="text-xs text-blue-400 mt-1">01020630677</p>
      </div>
    </div>
  );
};

// Inventory Management Component
const Inventory = () => {
  const [inventoryItems, setInventoryItems] = useState([]);
  const [inventoryTransactions, setInventoryTransactions] = useState([]);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [currentView, setCurrentView] = useState('items'); // items, transactions, low-stock, add-item
  const [editingItem, setEditingItem] = useState(null); // للتعديل
  const [newItem, setNewItem] = useState({
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    available_pieces: '',  // تغيير من available_height إلى available_pieces
    min_stock_level: 2,    // الحد الأدنى 2 قطعة
    notes: ''
  });
  const [newTransaction, setNewTransaction] = useState({
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    transaction_type: 'in',
    pieces_change: '',     // تغيير من height_change إلى pieces_change
    reason: '',
    notes: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  const materialTypes = ['NBR', 'BUR', 'BT', 'VT', 'BOOM'];

  // Fetch functions
  const fetchInventoryItems = async () => {
    try {
      const response = await axios.get(`${API}/inventory`);
      setInventoryItems(response.data || []);
    } catch (error) {
      console.error('Error fetching inventory items:', error);
    }
  };

  const fetchInventoryTransactions = async () => {
    try {
      const response = await axios.get(`${API}/inventory-transactions`);
      setInventoryTransactions(response.data || []);
    } catch (error) {
      console.error('Error fetching inventory transactions:', error);
    }
  };

  const fetchLowStockItems = async () => {
    try {
      const response = await axios.get(`${API}/inventory/low-stock`);
      setLowStockItems(response.data || []);
    } catch (error) {
      console.error('Error fetching low stock items:', error);
    }
  };

  useEffect(() => {
    fetchInventoryItems();
    fetchInventoryTransactions();
    fetchLowStockItems();
  }, []);

  // Add or Update inventory item
  const addInventoryItem = async () => {
    if (!newItem.material_type || !newItem.inner_diameter || 
        !newItem.outer_diameter || !newItem.available_pieces) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      if (editingItem) {
        // Update existing item
        await axios.put(`${API}/inventory/${editingItem.id}`, {
          ...newItem,
          inner_diameter: parseFloat(newItem.inner_diameter),
          outer_diameter: parseFloat(newItem.outer_diameter),
          available_pieces: parseInt(newItem.available_pieces),
          min_stock_level: parseInt(newItem.min_stock_level || 2)
        });
        alert('تم تحديث عنصر الجرد بنجاح');
        setEditingItem(null);
      } else {
        // Add new item
        await axios.post(`${API}/inventory`, {
          ...newItem,
          inner_diameter: parseFloat(newItem.inner_diameter),
          outer_diameter: parseFloat(newItem.outer_diameter),
          available_pieces: parseInt(newItem.available_pieces),
          min_stock_level: parseInt(newItem.min_stock_level || 2)
        });
        alert('تم إضافة عنصر الجرد بنجاح');
      }
      
      fetchInventoryItems();
      fetchLowStockItems();
      setCurrentView('items');
      setNewItem({
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        available_pieces: '',
        min_stock_level: 2,
        notes: ''
      });
    } catch (error) {
      console.error('Error saving inventory item:', error);
      alert('حدث خطأ في حفظ عنصر الجرد: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Add inventory transaction
  const addInventoryTransaction = async () => {
    if (!newTransaction.material_type || !newTransaction.inner_diameter || 
        !newTransaction.outer_diameter || !newTransaction.pieces_change || !newTransaction.reason) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      const transactionData = {
        ...newTransaction,
        inner_diameter: parseFloat(newTransaction.inner_diameter),
        outer_diameter: parseFloat(newTransaction.outer_diameter),
        pieces_change: newTransaction.transaction_type === 'out' 
          ? -Math.abs(parseInt(newTransaction.pieces_change))
          : Math.abs(parseInt(newTransaction.pieces_change))
      };

      await axios.post(`${API}/inventory-transactions`, transactionData);
      
      fetchInventoryItems();
      fetchInventoryTransactions();
      fetchLowStockItems();
      setNewTransaction({
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        transaction_type: 'in',
        pieces_change: '',
        reason: '',
        notes: ''
      });
      alert('تم تسجيل معاملة الجرد بنجاح');
    } catch (error) {
      console.error('Error adding inventory transaction:', error);
      alert('حدث خطأ في تسجيل معاملة الجرد: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Filter and sort items based on search
  const filteredItems = inventoryItems.filter(item =>
    item.material_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.inner_diameter.toString().includes(searchTerm.toLowerCase()) ||
    item.outer_diameter.toString().includes(searchTerm.toLowerCase()) ||
    item.notes?.toLowerCase().includes(searchTerm.toLowerCase())
  ).sort((a, b) => {
    // ترتيب حسب أولوية الخامة: BUR-NBR-BT-BOOM-VT
    const materialPriority = { 'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5 };
    const aPriority = materialPriority[a.material_type] || 6;
    const bPriority = materialPriority[b.material_type] || 6;
    
    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }
    // ثم ترتيب حسب المقاس (القطر الداخلي ثم الخارجي)
    if (a.inner_diameter !== b.inner_diameter) {
      return a.inner_diameter - b.inner_diameter;
    }
    return a.outer_diameter - b.outer_diameter;
  });

  const filteredTransactions = inventoryTransactions.filter(transaction =>
    transaction.reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
    transaction.material_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    transaction.notes?.toLowerCase().includes(searchTerm.toLowerCase())
  ).sort((a, b) => {
    // ترتيب حسب أولوية الخامة: BUR-NBR-BT-BOOM-VT
    const materialPriority = { 'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5 };
    const aPriority = materialPriority[a.material_type] || 6;
    const bPriority = materialPriority[b.material_type] || 6;
    
    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }
    // ثم ترتيب حسب المقاس (القطر الداخلي ثم الخارجي) ثم التاريخ
    if (a.inner_diameter !== b.inner_diameter) {
      return a.inner_diameter - b.inner_diameter;
    }
    if (a.outer_diameter !== b.outer_diameter) {
      return a.outer_diameter - b.outer_diameter;
    }
    return new Date(b.date) - new Date(a.date); // الأحدث أولاً
  });

  return (
    <div className="p-6" dir="rtl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">إدارة الجرد</h1>
        <div className="flex space-x-4 space-x-reverse">
          <button
            onClick={() => setCurrentView('items')}
            className={`px-4 py-2 rounded ${currentView === 'items' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            عناصر الجرد
          </button>
          <button
            onClick={() => setCurrentView('transactions')}
            className={`px-4 py-2 rounded ${currentView === 'transactions' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            معاملات الجرد
          </button>
          <button
            onClick={() => setCurrentView('low-stock')}
            className={`px-4 py-2 rounded ${currentView === 'low-stock' ? 'bg-red-500 text-white' : 'bg-gray-200'}`}
          >
            مخزون منخفض ({lowStockItems.length})
          </button>
          <button
            onClick={() => setCurrentView('excel')}
            className={`px-4 py-2 rounded ${currentView === 'excel' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}
          >
            إدارة الإكسل
          </button>
          <button
            onClick={() => setCurrentView('add-item')}
            className={`px-4 py-2 rounded ${currentView === 'add-item' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}
          >
            إضافة عنصر جديد
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="البحث في الجرد..."
          className="w-full p-3 border border-gray-300 rounded-lg"
        />
      </div>

      {/* Inventory Items View */}
      {currentView === 'items' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">عناصر الجرد</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-2">نوع المادة</th>
                  <th className="border border-gray-300 p-2">القطر الداخلي</th>
                  <th className="border border-gray-300 p-2">القطر الخارجي</th>
                  <th className="border border-gray-300 p-2">عدد القطع المتاحة</th>
                  <th className="border border-gray-300 p-2">الحد الأدنى</th>
                  <th className="border border-gray-300 p-2">الحالة</th>
                  <th className="border border-gray-300 p-2">ملاحظات</th>
                  <th className="border border-gray-300 p-2">الإجراءات</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map(item => (
                  <tr key={item.id}>
                    <td className="border border-gray-300 p-2 font-semibold">{item.material_type}</td>
                    <td className="border border-gray-300 p-2">{item.inner_diameter}</td>
                    <td className="border border-gray-300 p-2">{item.outer_diameter}</td>
                    <td className={`border border-gray-300 p-2 font-semibold ${
                      item.available_pieces <= item.min_stock_level ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {item.available_pieces} قطعة
                    </td>
                    <td className="border border-gray-300 p-2">{item.min_stock_level} قطعة</td>
                    <td className="border border-gray-300 p-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        item.available_pieces <= item.min_stock_level ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {item.available_pieces <= item.min_stock_level ? 'منخفض' : 'طبيعي'}
                      </span>
                    </td>
                    <td className="border border-gray-300 p-2">{item.notes || '-'}</td>
                    <td className="border border-gray-300 p-2">
                      <div className="flex space-x-2 space-x-reverse">
                        <button
                          onClick={() => {
                            setEditingItem(item);
                            setNewItem({
                              material_type: item.material_type,
                              inner_diameter: item.inner_diameter,
                              outer_diameter: item.outer_diameter,
                              available_pieces: item.available_pieces,
                              min_stock_level: item.min_stock_level,
                              notes: item.notes || ''
                            });
                            setCurrentView('add-item');
                          }}
                          className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                        >
                          تعديل
                        </button>
                        <button
                          onClick={async () => {
                            if (confirm('هل أنت متأكد من حذف هذا العنصر؟')) {
                              try {
                                await axios.delete(`${API}/inventory/${item.id}`);
                                alert('تم حذف العنصر بنجاح');
                                fetchInventoryItems();
                              } catch (error) {
                                console.error('Error deleting item:', error);
                                alert('حدث خطأ في حذف العنصر');
                              }
                            }
                          }}
                          className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                        >
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
      )}

      {/* Transactions View */}
      {currentView === 'transactions' && (
        <div>
          {/* Add Transaction Form */}
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-4">إضافة معاملة جرد</h3>
            <div className="grid grid-cols-3 gap-4">
              <select
                value={newTransaction.material_type}
                onChange={(e) => setNewTransaction({...newTransaction, material_type: e.target.value})}
                className="p-2 border border-gray-300 rounded"
              >
                {materialTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <input
                type="number"
                value={newTransaction.inner_diameter}
                onChange={(e) => setNewTransaction({...newTransaction, inner_diameter: e.target.value})}
                placeholder="القطر الداخلي"
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="number"
                value={newTransaction.outer_diameter}
                onChange={(e) => setNewTransaction({...newTransaction, outer_diameter: e.target.value})}
                placeholder="القطر الخارجي"
                className="p-2 border border-gray-300 rounded"
              />
              <select
                value={newTransaction.transaction_type}
                onChange={(e) => setNewTransaction({...newTransaction, transaction_type: e.target.value})}
                className="p-2 border border-gray-300 rounded"
              >
                <option value="in">إضافة للمخزون</option>
                <option value="out">خصم من المخزون</option>
              </select>
              <input
                type="number"
                step="1"
                value={newTransaction.pieces_change}
                onChange={(e) => setNewTransaction({...newTransaction, pieces_change: e.target.value})}
                placeholder="عدد القطع"
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="text"
                value={newTransaction.reason}
                onChange={(e) => setNewTransaction({...newTransaction, reason: e.target.value})}
                placeholder="سبب المعاملة"
                className="p-2 border border-gray-300 rounded"
              />
            </div>
            <div className="mt-4">
              <input
                type="text"
                value={newTransaction.notes}
                onChange={(e) => setNewTransaction({...newTransaction, notes: e.target.value})}
                placeholder="ملاحظات (اختياري)"
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            <button
              onClick={addInventoryTransaction}
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              تسجيل المعاملة
            </button>
          </div>

          {/* Transactions List */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">سجل معاملات الجرد</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 p-2">التاريخ</th>
                    <th className="border border-gray-300 p-2">نوع المادة</th>
                    <th className="border border-gray-300 p-2">المقاسات</th>
                    <th className="border border-gray-300 p-2">نوع المعاملة</th>
                    <th className="border border-gray-300 p-2">عدد القطع</th>
                    <th className="border border-gray-300 p-2">الرصيد المتبقي</th>
                    <th className="border border-gray-300 p-2">السبب</th>
                    <th className="border border-gray-300 p-2">ملاحظات</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTransactions.map(transaction => (
                    <tr key={transaction.id}>
                      <td className="border border-gray-300 p-2">
                        {new Date(transaction.date).toLocaleDateString('ar-EG')}
                      </td>
                      <td className="border border-gray-300 p-2">{transaction.material_type}</td>
                      <td className="border border-gray-300 p-2">
                        {transaction.inner_diameter} × {transaction.outer_diameter}
                      </td>
                      <td className="border border-gray-300 p-2">
                        <span className={`px-2 py-1 rounded text-sm ${
                          transaction.transaction_type === 'in' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {transaction.transaction_type === 'in' ? 'إضافة' : 'خصم'}
                        </span>
                      </td>
                      <td className={`border border-gray-300 p-2 font-semibold ${
                        transaction.pieces_change > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {transaction.pieces_change > 0 ? '+' : ''}{transaction.pieces_change} قطعة
                      </td>
                      <td className="border border-gray-300 p-2 font-semibold">
                        {transaction.remaining_pieces} قطعة
                      </td>
                      <td className="border border-gray-300 p-2">{transaction.reason}</td>
                      <td className="border border-gray-300 p-2">{transaction.notes || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Low Stock Items View */}
      {currentView === 'low-stock' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4 text-red-600">
            عناصر بمخزون منخفض ({lowStockItems.length})
          </h3>
          {lowStockItems.length === 0 ? (
            <p className="text-green-600 text-center py-8">
              ✅ جميع عناصر الجرد في المستوى الطبيعي
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-red-50">
                    <th className="border border-gray-300 p-2">نوع المادة</th>
                    <th className="border border-gray-300 p-2">المقاسات</th>
                    <th className="border border-gray-300 p-2">المخزون الحالي</th>
                    <th className="border border-gray-300 p-2">الحد الأدنى</th>
                    <th className="border border-gray-300 p-2">نقص المخزون</th>
                  </tr>
                </thead>
                <tbody>
                  {lowStockItems.map(item => (
                    <tr key={item.id} className="bg-red-50">
                      <td className="border border-gray-300 p-2 font-semibold">{item.material_type}</td>
                      <td className="border border-gray-300 p-2">
                        {item.inner_diameter} × {item.outer_diameter}
                      </td>
                      <td className="border border-gray-300 p-2 font-semibold text-red-600">
                        {item.available_pieces} قطعة
                      </td>
                      <td className="border border-gray-300 p-2">{item.min_stock_level} قطعة</td>
                      <td className="border border-gray-300 p-2 font-semibold text-red-600">
                        {Math.max(0, item.min_stock_level - item.available_pieces)} قطعة
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Add/Edit Item View */}
      {currentView === 'add-item' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">
            {editingItem ? 'تعديل عنصر الجرد' : 'إضافة عنصر جرد جديد'}
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <select
              value={newItem.material_type}
              onChange={(e) => setNewItem({...newItem, material_type: e.target.value})}
              className="p-2 border border-gray-300 rounded"
            >
              {materialTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <input
              type="number"
              value={newItem.inner_diameter}
              onChange={(e) => setNewItem({...newItem, inner_diameter: e.target.value})}
              placeholder="القطر الداخلي"
              className="p-2 border border-gray-300 rounded"
            />
            <input
              type="number"
              value={newItem.outer_diameter}
              onChange={(e) => setNewItem({...newItem, outer_diameter: e.target.value})}
              placeholder="القطر الخارجي"
              className="p-2 border border-gray-300 rounded"
            />
            <input
              type="number"
              step="1"
              value={newItem.available_pieces}
              onChange={(e) => setNewItem({...newItem, available_pieces: e.target.value})}
              placeholder="عدد القطع المتاحة"
              className="p-2 border border-gray-300 rounded"
            />
            <input
              type="number"
              value={newItem.min_stock_level}
              onChange={(e) => setNewItem({...newItem, min_stock_level: e.target.value})}
              placeholder="الحد الأدنى للمخزون"
              className="p-2 border border-gray-300 rounded"
            />
            <input
              type="text"
              value={newItem.notes}
              onChange={(e) => setNewItem({...newItem, notes: e.target.value})}
              placeholder="ملاحظات (اختياري)"
              className="p-2 border border-gray-300 rounded"
            />
          </div>
          <button
            onClick={addInventoryItem}
            className="mt-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            {editingItem ? 'تحديث عنصر الجرد' : 'إضافة عنصر الجرد'}
          </button>
          {editingItem && (
            <button
              onClick={() => {
                setEditingItem(null);
                setNewItem({
                  material_type: 'NBR',
                  inner_diameter: '',
                  outer_diameter: '',
                  available_pieces: '',
                  min_stock_level: 2,
                  notes: ''
                });
                setCurrentView('items');
              }}
              className="mt-4 mr-2 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              إلغاء التعديل
            </button>
          )}
        </div>
      )}

      {/* Excel Management View */}
      {currentView === 'excel' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Inventory Excel Management */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">إدارة ملفات الجرد - Excel</h3>
            
            {/* Export Inventory */}
            <div className="mb-6">
              <h4 className="font-medium mb-2">تصدير بيانات الجرد</h4>
              <button
                onClick={async () => {
                  try {
                    const response = await axios.get(`${API}/excel/export/inventory`, {
                      responseType: 'blob'
                    });
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', `inventory_export_${new Date().toISOString().split('T')[0]}.xlsx`);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    alert('تم تصدير ملف الجرد بنجاح');
                  } catch (error) {
                    console.error('Error exporting inventory:', error);
                    alert('حدث خطأ في تصدير الملف');
                  }
                }}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                تصدير جرد Excel
              </button>
            </div>

            {/* Import Inventory */}
            <div>
              <h4 className="font-medium mb-2">استيراد بيانات الجرد</h4>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={async (e) => {
                  const file = e.target.files[0];
                  if (!file) return;
                  
                  const formData = new FormData();
                  formData.append('file', file);
                  
                  try {
                    const response = await axios.post(`${API}/excel/import/inventory`, formData, {
                      headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    alert(`تم استيراد ${response.data.imported_count} عنصر بنجاح`);
                    if (response.data.errors.length > 0) {
                      console.warn('Import errors:', response.data.errors);
                    }
                    fetchInventoryItems();
                  } catch (error) {
                    console.error('Error importing inventory:', error);
                    alert('حدث خطأ في استيراد الملف');
                  }
                  
                  e.target.value = '';
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
              />
              <p className="text-sm text-gray-600 mt-2">
                الأعمدة المطلوبة: material_type, inner_diameter, outer_diameter, available_pieces
              </p>
            </div>
          </div>

          {/* Raw Materials Excel Management */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">إدارة المواد الخام - Excel</h3>
            
            {/* Export Raw Materials */}
            <div className="mb-6">
              <h4 className="font-medium mb-2">تصدير المواد الخام</h4>
              <button
                onClick={async () => {
                  try {
                    const response = await axios.get(`${API}/excel/export/raw-materials`, {
                      responseType: 'blob'
                    });
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', `raw_materials_export_${new Date().toISOString().split('T')[0]}.xlsx`);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    alert('تم تصدير ملف المواد الخام بنجاح');
                  } catch (error) {
                    console.error('Error exporting raw materials:', error);
                    alert('حدث خطأ في تصدير الملف');
                  }
                }}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                تصدير مواد خام Excel
              </button>
            </div>

            {/* Import Raw Materials */}
            <div>
              <h4 className="font-medium mb-2">استيراد المواد الخام</h4>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={async (e) => {
                  const file = e.target.files[0];
                  if (!file) return;
                  
                  const formData = new FormData();
                  formData.append('file', file);
                  
                  try {
                    const response = await axios.post(`${API}/excel/import/raw-materials`, formData, {
                      headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    alert(`تم استيراد ${response.data.imported_count} مادة خام بنجاح`);
                    if (response.data.errors.length > 0) {
                      console.warn('Import errors:', response.data.errors);
                    }
                  } catch (error) {
                    console.error('Error importing raw materials:', error);
                    alert('حدث خطأ في استيراد الملف');
                  }
                  
                  e.target.value = '';
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
              />
              <p className="text-sm text-gray-600 mt-2">
                الأعمدة المطلوبة: material_type, inner_diameter, outer_diameter, height, pieces_count, unit_code, cost_per_mm
              </p>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-yellow-50 p-6 rounded-lg shadow-md md:col-span-2">
            <h3 className="text-lg font-semibold mb-4">تعليمات استخدام الإكسل</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">تصدير البيانات:</h4>
                <ul className="text-sm text-gray-700 list-disc list-inside space-y-1">
                  <li>يتم تصدير جميع البيانات الحالية</li>
                  <li>الملف يحتوي على تنسيق جاهز للتعديل</li>
                  <li>يمكن فتح الملف في Excel أو Google Sheets</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">استيراد البيانات:</h4>
                <ul className="text-sm text-gray-700 list-disc list-inside space-y-1">
                  <li>يجب أن يكون الملف من نوع .xlsx أو .xls</li>
                  <li>الأعمدة المطلوبة يجب أن تكون موجودة</li>
                  <li>البيانات الموجودة لن تتأثر (يتم التحديث أو الإضافة)</li>
                  <li>سيتم عرض رسالة تأكيد مع عدد العناصر المستوردة</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Local Products Management Component
const Local = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [localProducts, setLocalProducts] = useState([]);
  const [supplierTransactions, setSupplierTransactions] = useState([]);
  const [currentView, setCurrentView] = useState('suppliers'); // suppliers, products, transactions
  const [newSupplier, setNewSupplier] = useState({ name: '', phone: '', address: '' });
  const [newProduct, setNewProduct] = useState({ name: '', supplier_id: '', purchase_price: '', selling_price: '', current_stock: 0 });
  const [newTransaction, setNewTransaction] = useState({ supplier_id: '', transaction_type: 'purchase', amount: '', description: '', product_name: '', quantity: '', unit_price: '', payment_method: 'cash' });
  const [selectedSupplier, setSelectedSupplier] = useState('');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');

  // Fetch data functions
  const fetchSuppliers = async () => {
    try {
      const response = await axios.get(`${API}/suppliers`);
      setSuppliers(response.data || []);
    } catch (error) {
      console.error('Error fetching suppliers:', error);
    }
  };

  const fetchLocalProducts = async () => {
    try {
      const response = await axios.get(`${API}/local-products`);
      setLocalProducts(response.data || []);
    } catch (error) {
      console.error('Error fetching local products:', error);
    }
  };

  const fetchSupplierTransactions = async () => {
    try {
      const response = await axios.get(`${API}/supplier-transactions`);
      setSupplierTransactions(response.data || []);
    } catch (error) {
      console.error('Error fetching supplier transactions:', error);
    }
  };

  useEffect(() => {
    fetchSuppliers();
    fetchLocalProducts();
    fetchSupplierTransactions();
  }, []);

  // Add supplier
  const addSupplier = async () => {
    if (!newSupplier.name.trim()) {
      alert('الرجاء إدخال اسم المورد');
      return;
    }

    try {
      if (newSupplier.id) {
        // Update existing supplier
        await axios.put(`${API}/suppliers/${newSupplier.id}`, {
          name: newSupplier.name,
          phone: newSupplier.phone,
          address: newSupplier.address
        });
        alert('تم تحديث المورد بنجاح');
      } else {
        // Add new supplier
        await axios.post(`${API}/suppliers`, newSupplier);
        alert('تم إضافة المورد بنجاح');
      }
      
      fetchSuppliers();
      setNewSupplier({ name: '', phone: '', address: '' });
    } catch (error) {
      console.error('Error saving supplier:', error);
      alert('حدث خطأ في حفظ المورد: ' + (error.response?.data?.detail || error.message));
    }
  };

  const editSupplier = (supplier) => {
    // Fill the form with supplier data for editing
    setNewSupplier({
      id: supplier.id,
      name: supplier.name,
      phone: supplier.phone || '',
      address: supplier.address || ''
    });
  };

  const deleteSupplier = async (supplierId) => {
    if (!confirm('هل أنت متأكد من حذف هذا المورد؟ سيتم حذف جميع البيانات المرتبطة به.')) {
      return;
    }

    try {
      await axios.delete(`${API}/suppliers/${supplierId}`);
      fetchSuppliers();
      fetchLocalProducts(); // Refresh products as they might be affected
      alert('تم حذف المورد بنجاح');
    } catch (error) {
      console.error('Error deleting supplier:', error);
      alert('حدث خطأ في حذف المورد: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Add local product
  const addLocalProduct = async () => {
    if (!newProduct.name.trim() || !newProduct.supplier_id || !newProduct.purchase_price || !newProduct.selling_price) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      if (newProduct.id) {
        // Update existing product
        await axios.put(`${API}/local-products/${newProduct.id}`, {
          name: newProduct.name,
          supplier_id: newProduct.supplier_id,
          purchase_price: parseFloat(newProduct.purchase_price),
          selling_price: parseFloat(newProduct.selling_price),
          current_stock: parseInt(newProduct.current_stock || 0)
        });
        alert('تم تحديث المنتج بنجاح');
      } else {
        // Add new product
        await axios.post(`${API}/local-products`, {
          ...newProduct,
          purchase_price: parseFloat(newProduct.purchase_price),
          selling_price: parseFloat(newProduct.selling_price),
          current_stock: parseInt(newProduct.current_stock || 0)
        });
        alert('تم إضافة المنتج بنجاح');
      }
      
      fetchLocalProducts();
      setNewProduct({ name: '', supplier_id: '', purchase_price: '', selling_price: '', current_stock: 0 });
    } catch (error) {
      console.error('Error saving local product:', error);
      alert('حدث خطأ في حفظ المنتج: ' + (error.response?.data?.detail || error.message));
    }
  };

  const editLocalProduct = (product) => {
    // Fill the form with product data for editing
    setNewProduct({
      id: product.id,
      name: product.name,
      supplier_id: product.supplier_id,
      purchase_price: product.purchase_price.toString(),
      selling_price: product.selling_price.toString(),
      current_stock: product.current_stock || 0
    });
  };

  const deleteLocalProduct = async (productId) => {
    if (!confirm('هل أنت متأكد من حذف هذا المنتج المحلي؟ سيتم حذف جميع البيانات المرتبطة به.')) {
      return;
    }

    try {
      await axios.delete(`${API}/local-products/${productId}`);
      fetchLocalProducts();
      alert('تم حذف المنتج المحلي بنجاح');
    } catch (error) {
      console.error('Error deleting local product:', error);
      alert('حدث خطأ في حذف المنتج: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Pay supplier
  const paySupplier = async () => {
    if (!selectedSupplier || !paymentAmount) {
      alert('الرجاء اختيار المورد وإدخال المبلغ');
      return;
    }

    try {
      await axios.post(`${API}/supplier-payment?supplier_id=${selectedSupplier}&amount=${paymentAmount}&payment_method=${paymentMethod}`);
      fetchSuppliers();
      fetchSupplierTransactions();
      setSelectedSupplier('');
      setPaymentAmount('');
      alert('تم دفع المبلغ للمورد بنجاح');
    } catch (error) {
      console.error('Error paying supplier:', error);
      alert('حدث خطأ في دفع المبلغ');
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">إدارة المنتجات المحلية</h1>
        <div className="flex space-x-4 space-x-reverse">
          <button
            onClick={() => setCurrentView('suppliers')}
            className={`px-4 py-2 rounded ${currentView === 'suppliers' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            الموردين
          </button>
          <button
            onClick={() => setCurrentView('products')}
            className={`px-4 py-2 rounded ${currentView === 'products' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            المنتجات
          </button>
          <button
            onClick={() => setCurrentView('transactions')}
            className={`px-4 py-2 rounded ${currentView === 'transactions' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            المعاملات
          </button>
          <button
            onClick={() => setCurrentView('payments')}
            className={`px-4 py-2 rounded ${currentView === 'payments' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            سداد الموردين
          </button>
        </div>
      </div>

      {/* Suppliers View */}
      {currentView === 'suppliers' && (
        <div>
          {/* Add New Supplier */}
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-4">إضافة مورد جديد</h3>
            <div className="grid grid-cols-3 gap-4">
              <input
                type="text"
                value={newSupplier.name}
                onChange={(e) => setNewSupplier({...newSupplier, name: e.target.value})}
                placeholder="اسم المورد"
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="text"
                value={newSupplier.phone}
                onChange={(e) => setNewSupplier({...newSupplier, phone: e.target.value})}
                placeholder="رقم الهاتف (اختياري)"
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="text"
                value={newSupplier.address}
                onChange={(e) => setNewSupplier({...newSupplier, address: e.target.value})}
                placeholder="العنوان (اختياري)"
                className="p-2 border border-gray-300 rounded"
              />
            </div>
            <button
              onClick={addSupplier}
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              إضافة المورد
            </button>
          </div>

          {/* Suppliers List */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">قائمة الموردين</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 p-2">اسم المورد</th>
                    <th className="border border-gray-300 p-2">الهاتف</th>
                    <th className="border border-gray-300 p-2">العنوان</th>
                    <th className="border border-gray-300 p-2">إجمالي المشتريات</th>
                    <th className="border border-gray-300 p-2">إجمالي المدفوع</th>
                    <th className="border border-gray-300 p-2">الرصيد المستحق</th>
                    <th className="border border-gray-300 p-2">إجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {suppliers.map(supplier => (
                    <tr key={supplier.id}>
                      <td className="border border-gray-300 p-2 font-semibold">{supplier.name}</td>
                      <td className="border border-gray-300 p-2">{supplier.phone || '-'}</td>
                      <td className="border border-gray-300 p-2">{supplier.address || '-'}</td>
                      <td className="border border-gray-300 p-2">ج.م {(supplier.total_purchases || 0).toFixed(2)}</td>
                      <td className="border border-gray-300 p-2">ج.م {(supplier.total_paid || 0).toFixed(2)}</td>
                      <td className={`border border-gray-300 p-2 font-semibold ${(supplier.balance || 0) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        ج.م {(supplier.balance || 0).toFixed(2)}
                      </td>
                      <td className="border border-gray-300 p-2">
                        <div className="flex space-x-2 space-x-reverse">
                          <button
                            onClick={() => editSupplier(supplier)}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                            title="تحرير"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => deleteSupplier(supplier.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                            title="حذف"
                          >
                            🗑️
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
      )}

      {/* Products View */}
      {currentView === 'products' && (
        <div>
          {/* Add New Product */}
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-4">إضافة منتج محلي جديد</h3>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="text"
                value={newProduct.name}
                onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                placeholder="اسم المنتج"
                className="p-2 border border-gray-300 rounded"
              />
              <select
                value={newProduct.supplier_id}
                onChange={(e) => setNewProduct({...newProduct, supplier_id: e.target.value})}
                className="p-2 border border-gray-300 rounded"
              >
                <option value="">اختر المورد</option>
                {suppliers.map(supplier => (
                  <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
                ))}
              </select>
              <input
                type="number"
                step="0.01"
                value={newProduct.purchase_price}
                onChange={(e) => setNewProduct({...newProduct, purchase_price: e.target.value})}
                placeholder="سعر الشراء"
                className="p-2 border border-gray-300 rounded"
              />
              <input
                type="number"
                step="0.01"
                value={newProduct.selling_price}
                onChange={(e) => setNewProduct({...newProduct, selling_price: e.target.value})}
                placeholder="سعر البيع"
                className="p-2 border border-gray-300 rounded"
              />
            </div>
            <button
              onClick={addLocalProduct}
              className="mt-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              إضافة المنتج
            </button>
          </div>

          {/* Products List */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">قائمة المنتجات المحلية</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 p-2">اسم المنتج</th>
                    <th className="border border-gray-300 p-2">المورد</th>
                    <th className="border border-gray-300 p-2">سعر الشراء</th>
                    <th className="border border-gray-300 p-2">سعر البيع</th>
                    <th className="border border-gray-300 p-2">المخزون الحالي</th>
                    <th className="border border-gray-300 p-2">إجمالي المباع</th>
                    <th className="border border-gray-300 p-2">إجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {localProducts.map(product => (
                    <tr key={product.id}>
                      <td className="border border-gray-300 p-2 font-semibold">{product.name}</td>
                      <td className="border border-gray-300 p-2">{product.supplier_name}</td>
                      <td className="border border-gray-300 p-2">ج.م {product.purchase_price.toFixed(2)}</td>
                      <td className="border border-gray-300 p-2">ج.م {product.selling_price.toFixed(2)}</td>
                      <td className="border border-gray-300 p-2">{product.current_stock || 0}</td>
                      <td className="border border-gray-300 p-2">{product.total_sold || 0}</td>
                      <td className="border border-gray-300 p-2">
                        <div className="flex space-x-2 space-x-reverse">
                          <button
                            onClick={() => editLocalProduct(product)}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                            title="تحرير"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => deleteLocalProduct(product.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                            title="حذف"
                          >
                            🗑️
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
      )}

      {/* Transactions View */}
      {currentView === 'transactions' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">معاملات الموردين</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-2">التاريخ</th>
                  <th className="border border-gray-300 p-2">المورد</th>
                  <th className="border border-gray-300 p-2">نوع المعاملة</th>
                  <th className="border border-gray-300 p-2">المبلغ</th>
                  <th className="border border-gray-300 p-2">الوصف</th>
                  <th className="border border-gray-300 p-2">المنتج</th>
                  <th className="border border-gray-300 p-2">الكمية</th>
                </tr>
              </thead>
              <tbody>
                {supplierTransactions.map(transaction => (
                  <tr key={transaction.id}>
                    <td className="border border-gray-300 p-2">
                      {new Date(transaction.date).toLocaleDateString('ar-EG')}
                    </td>
                    <td className="border border-gray-300 p-2">{transaction.supplier_name}</td>
                    <td className="border border-gray-300 p-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        transaction.transaction_type === 'purchase' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {transaction.transaction_type === 'purchase' ? 'شراء' : 'دفع'}
                      </span>
                    </td>
                    <td className={`border border-gray-300 p-2 font-semibold ${
                      transaction.transaction_type === 'purchase' ? 'text-red-600' : 'text-green-600'
                    }`}>
                      ج.م {transaction.amount.toFixed(2)}
                    </td>
                    <td className="border border-gray-300 p-2">{transaction.description}</td>
                    <td className="border border-gray-300 p-2">{transaction.product_name || '-'}</td>
                    <td className="border border-gray-300 p-2">{transaction.quantity || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payments View */}
      {currentView === 'payments' && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">سداد حسابات الموردين</h3>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <select
              value={selectedSupplier}
              onChange={(e) => setSelectedSupplier(e.target.value)}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="">اختر المورد</option>
              {suppliers.filter(s => (s.balance || 0) > 0).map(supplier => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name} - مستحق: ج.م {(supplier.balance || 0).toFixed(2)}
                </option>
              ))}
            </select>
            <input
              type="number"
              step="0.01"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(e.target.value)}
              placeholder="المبلغ المدفوع"
              className="p-2 border border-gray-300 rounded"
            />
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="cash">نقدي</option>
              <option value="vodafone_elsawy">فودافون كاش الصاوي</option>
              <option value="vodafone_wael">فودافون كاش وائل</option>
              <option value="instapay">انستا باي</option>
            </select>
          </div>
          <button
            onClick={paySupplier}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            دفع المبلغ
          </button>
        </div>
      )}
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user } = useAuth();
  
  // Only Elsawy can access dashboard
  if (user?.username !== 'Elsawy') {
    return (
      <div className="p-6" dir="rtl">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>غير مسموح!</strong> لوحة التحكم مخصصة للمستخدم Elsawy فقط.
        </div>
      </div>
    );
  }

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

  const clearAllData = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع البيانات؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    try {
      // Clear all data from backend
      await axios.delete(`${API}/customers/clear-all`);
      await axios.delete(`${API}/raw-materials/clear-all`);
      await axios.delete(`${API}/finished-products/clear-all`);
      await axios.delete(`${API}/invoices/clear-all`);
      await axios.delete(`${API}/expenses/clear-all`);
      await axios.delete(`${API}/payments/clear-all`);
      await axios.delete(`${API}/work-orders/clear-all`);
      
      // Refresh dashboard stats
      fetchStats();
      
      alert('تم حذف جميع البيانات');
    } catch (error) {
      console.error('Error clearing all data:', error);
      alert('حدث خطأ في حذف البيانات');
    }
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
    <div className="space-y-6" dir="rtl">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">لوحة التحكم</h2>
            <p className="text-blue-100">مرحباً {user?.username} - إليك نظرة عامة على أداء النشاط</p>
          </div>
          <div className="text-6xl opacity-20">📊</div>
        </div>
        
        <div className="flex flex-wrap space-x-4 space-x-reverse mt-6">
          <button 
            onClick={clearAllData}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl hover:transform hover:scale-105">
            🗑️ حذف الكل
          </button>
          <button 
            onClick={fetchStats}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl hover:transform hover:scale-105">
            🔄 إعادة تحميل
          </button>
          <button 
            onClick={() => printReport('dashboard')}
            className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl hover:transform hover:scale-105">
            🖨️ طباعة تقرير
          </button>
          <select className="bg-white text-gray-700 border-0 rounded-lg px-4 py-3 shadow-lg focus:ring-2 focus:ring-blue-300 font-medium">
            <option>📅 يومي</option>
            <option>📆 أسبوعي</option>
            <option>📊 شهري</option>
            <option>📈 سنوي</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total Sales */}
        <div className="bg-gradient-to-br from-green-400 to-green-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">إجمالي المبيعات</h3>
              <p className="text-3xl font-bold mt-2">
                ج.م {stats.total_sales.toFixed(2)}
              </p>
            </div>
            <div className="text-5xl opacity-30">💰</div>
          </div>
        </div>
        
        {/* Total Expenses */}
        <div className="bg-gradient-to-br from-red-400 to-red-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">إجمالي المصروفات</h3>
              <p className="text-3xl font-bold mt-2">
                ج.م {stats.total_expenses.toFixed(2)}
              </p>
            </div>
            <div className="text-5xl opacity-30">💸</div>
          </div>
        </div>
        
        {/* Net Profit */}
        <div className="bg-gradient-to-br from-blue-400 to-blue-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">صافي الربح</h3>
              <p className="text-3xl font-bold mt-2">
                ج.م {stats.net_profit.toFixed(2)}
              </p>
            </div>
            <div className="text-5xl opacity-30">📈</div>
          </div>
        </div>
        
        {/* Unpaid Amount */}
        <div className="bg-gradient-to-br from-orange-400 to-orange-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">المبالغ المستحقة</h3>
              <p className="text-3xl font-bold mt-2">
                ج.م {stats.total_unpaid.toFixed(2)}
              </p>
            </div>
            <div className="text-5xl opacity-30">⏳</div>
          </div>
        </div>
        
        {/* Invoice Count */}
        <div className="bg-gradient-to-br from-purple-400 to-purple-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">عدد الفواتير</h3>
              <p className="text-3xl font-bold mt-2">
                {stats.invoice_count}
              </p>
            </div>
            <div className="text-5xl opacity-30">🧾</div>
          </div>
        </div>
        
        {/* Customer Count */}
        <div className="bg-gradient-to-br from-teal-400 to-teal-600 p-6 rounded-xl text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:transform hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold opacity-90">عدد العملاء</h3>
              <p className="text-3xl font-bold mt-2">
                {stats.customer_count}
              </p>
            </div>
            <div className="text-5xl opacity-30">👥</div>
          </div>
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
  const [supervisorName, setSupervisorName] = useState(''); // اسم المشرف على التصنيع
  const [invoiceTitle, setInvoiceTitle] = useState(''); // عنوان الفاتورة
  const [currentItem, setCurrentItem] = useState({
    seal_type: 'RSL',
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    height: '',
    quantity: 1,
    unit_price: '',
    product_type: 'manufactured' // manufactured أو local
  });
  // New state for dual measurement inputs
  const [measurements, setMeasurements] = useState({
    inner_diameter_mm: '',
    inner_diameter_inch: '',
    outer_diameter_mm: '',
    outer_diameter_inch: '',
    height_mm: '',
    height_inch: '',
    wall_height_mm: '',
    wall_height_inch: ''
  });
  const [localProduct, setLocalProduct] = useState({
    product_size: '',      // مقاس المنتج
    product_type: '',      // نوع المنتج
    purchase_price: '',
    selling_price: '',
    supplier: ''
  });
  const [items, setItems] = useState([]);
  const [paymentMethod, setPaymentMethod] = useState('نقدي');
  const [discount, setDiscount] = useState(0); // الخصم
  const [discountType, setDiscountType] = useState('amount'); // نوع الخصم: amount أو percentage
  const [compatibilityResults, setCompatibilityResults] = useState(null);
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [selectedMaterials, setSelectedMaterials] = useState([]); // خامات متعددة مختارة
  const [measurementUnit, setMeasurementUnit] = useState('مم'); // بوصة أو مم
  const [wallHeight, setWallHeight] = useState(''); // ارتفاع الحيطة للـ W types
  const [clientType, setClientType] = useState(1); // نوع العميل للتسعير (1, 2, 3)

  // Measurement conversion functions
  const mmToInch = (mm) => {
    if (!mm || mm === '') return '';
    return (parseFloat(mm) / 25.4).toFixed(4);
  };

  const inchToMm = (inch) => {
    if (!inch || inch === '') return '';
    return (parseFloat(inch) * 25.4).toFixed(2);
  };

  // Handle measurement input changes with auto-conversion
  const handleMeasurementChange = (field, value, unit) => {
    const newMeasurements = { ...measurements };
    
    if (unit === 'mm') {
      newMeasurements[`${field}_mm`] = value;
      newMeasurements[`${field}_inch`] = mmToInch(value);
    } else {
      newMeasurements[`${field}_inch`] = value;
      newMeasurements[`${field}_mm`] = inchToMm(value);
    }
    
    setMeasurements(newMeasurements);
    
    // Update currentItem with mm values (for backend compatibility)
    const mmValue = parseFloat(newMeasurements[`${field}_mm`]) || '';
    setCurrentItem({
      ...currentItem,
      [field]: mmValue
    });
  };

  const sealTypes = ['RSL', 'RS', 'RSS', 'RSE', 'B17', 'B3', 'B14', 'B1', 'R15', 'R17', 'W1', 'W4', 'W5', 'W11', 'WBT', 'XR', 'CH', 'VR'];
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

  // Calculate automatic pricing based on material and client type
  const calculateAutomaticPrice = async (material, height, clientType) => {
    try {
      const response = await axios.post(`${API}/calculate-price`, null, {
        params: {
          material_type: material.material_type,
          inner_diameter: material.inner_diameter,
          outer_diameter: material.outer_diameter,
          height: height,
          client_type: clientType
        }
      });
      
      return response.data;
    } catch (error) {
      console.log('No pricing found for this material combination:', error);
      return null;
    }
  };

  // Confirm multi-material selection and calculate pricing
  const confirmMultiMaterialSelection = async () => {
    try {
      // Calculate total pricing for all selected materials
      let totalPrice = 0;
      const height = parseFloat(currentItem.height);
      
      for (const selected of selectedMaterials) {
        const pricing = await calculateAutomaticPrice(selected.material, height, clientType);
        if (pricing) {
          totalPrice += pricing.total_price * selected.seals;
        }
      }
      
      // Update the current item with the calculated price
      setCurrentItem({
        ...currentItem,
        unit_price: (totalPrice / parseInt(currentItem.quantity)).toFixed(2)
      });
      
      // Set the first material as the selected material for compatibility
      if (selectedMaterials.length > 0) {
        setSelectedMaterial(selectedMaterials[0].material);
      }
      
      alert(`✅ تم تأكيد اختيار الخامات بنجاح!

📊 ملخص الاختيار:
${selectedMaterials.map(sel => `- ${sel.material.unit_code}: ${sel.seals} سيل`).join('\n')}

💰 السعر الإجمالي: ${totalPrice.toFixed(2)} ج.م
💰 سعر السيل الواحد: ${(totalPrice / parseInt(currentItem.quantity)).toFixed(2)} ج.م`);
      
    } catch (error) {
      console.error('Error confirming multi-material selection:', error);
      alert('حدث خطأ في تأكيد الاختيار');
    }
  };

  const checkCompatibility = async () => {
    if (!currentItem.inner_diameter || !currentItem.outer_diameter || !currentItem.height) {
      alert('الرجاء إدخال جميع المقاسات المطلوبة');
      return;
    }
    
    let innerDiameter = parseFloat(currentItem.inner_diameter);
    let outerDiameter = parseFloat(currentItem.outer_diameter);
    let height = parseFloat(currentItem.height);
    
    if (isNaN(innerDiameter) || isNaN(outerDiameter) || isNaN(height)) {
      alert('الرجاء إدخال أرقام صحيحة للمقاسات');
      return;
    }
    
    // Convert from inches to millimeters if needed
    if (measurementUnit === 'بوصة') {
      innerDiameter = innerDiameter * 25.4;
      outerDiameter = outerDiameter * 25.4;
      height = height * 25.4;
      
      console.log(`تحويل من بوصة إلى ملليمتر:
        القطر الداخلي: ${currentItem.inner_diameter} بوصة = ${innerDiameter.toFixed(1)} مم
        القطر الخارجي: ${currentItem.outer_diameter} بوصة = ${outerDiameter.toFixed(1)} مم
        الارتفاع: ${currentItem.height} بوصة = ${height.toFixed(1)} مم`);
    }
    
    try {
      const response = await axios.post(`${API}/compatibility-check`, {
        seal_type: currentItem.seal_type,
        material_type: currentItem.material_type,
        inner_diameter: innerDiameter,
        outer_diameter: outerDiameter,
        height: height
      });
      setCompatibilityResults(response.data);
    } catch (error) {
      console.error('Error checking compatibility:', error);
      alert('حدث خطأ في فحص التوافق');
    }
  };

  const addItem = () => {
    if (currentItem.product_type === 'manufactured') {
      // Validation for manufactured products - check if at least one measurement is filled
      const hasInnerDiameter = measurements.inner_diameter_mm || measurements.inner_diameter_inch;
      const hasOuterDiameter = measurements.outer_diameter_mm || measurements.outer_diameter_inch;
      const hasHeight = measurements.height_mm || measurements.height_inch;
      
      if (!hasInnerDiameter || !hasOuterDiameter || !hasHeight || !currentItem.unit_price) {
        alert('الرجاء إدخال جميع البيانات المطلوبة (القياسات والسعر)');
        return;
      }

      // Use mm values (they're automatically kept in sync by handleMeasurementChange)
      const innerDiameter = parseFloat(currentItem.inner_diameter);
      const outerDiameter = parseFloat(currentItem.outer_diameter);
      const height = parseFloat(currentItem.height);
      const wallHeightValue = parseFloat(measurements.wall_height_mm) || null;

      const item = {
        ...currentItem,
        inner_diameter: innerDiameter,
        outer_diameter: outerDiameter,
        height: height,
        quantity: parseInt(currentItem.quantity),
        unit_price: parseFloat(currentItem.unit_price),
        total_price: parseFloat(currentItem.unit_price) * parseInt(currentItem.quantity),
        wall_height: wallHeightValue,
        // Store original display values for both units
        display_measurements: {
          inner_diameter_mm: measurements.inner_diameter_mm,
          inner_diameter_inch: measurements.inner_diameter_inch,
          outer_diameter_mm: measurements.outer_diameter_mm,
          outer_diameter_inch: measurements.outer_diameter_inch,
          height_mm: measurements.height_mm,
          height_inch: measurements.height_inch,
          wall_height_mm: measurements.wall_height_mm,
          wall_height_inch: measurements.wall_height_inch
        },
        material_used: selectedMaterial ? selectedMaterial.unit_code : null,
        material_details: selectedMaterial ? {
          id: selectedMaterial.id,
          unit_code: selectedMaterial.unit_code,
          inner_diameter: selectedMaterial.inner_diameter,
          outer_diameter: selectedMaterial.outer_diameter,
          height: selectedMaterial.height,
          material_type: selectedMaterial.material_type,
          is_finished_product: selectedMaterial.is_finished_product || false
        } : {
          // إرسال معلومات المادة الأساسية حتى بدون اختيار مادة محددة
          material_type: currentItem.material_type,
          inner_diameter: parseFloat(currentItem.inner_diameter),
          outer_diameter: parseFloat(currentItem.outer_diameter),
          is_finished_product: false
        },
        // إضافة معلومات الخامات المتعددة
        selected_materials: selectedMaterials.length > 0 ? selectedMaterials.map(sel => ({
          unit_code: sel.material.unit_code,
          material_type: sel.material.material_type,
          inner_diameter: sel.material.inner_diameter,
          outer_diameter: sel.material.outer_diameter,
          height: sel.material.height,
          seals_count: sel.seals,
          id: sel.material.id
        })) : null
      };

      setItems([...items, item]);
      setCurrentItem({
        seal_type: 'RSL',
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        quantity: 1,
        unit_price: '',
        product_type: 'manufactured'
      });
      setMeasurements({
        inner_diameter_mm: '',
        inner_diameter_inch: '',
        outer_diameter_mm: '',
        outer_diameter_inch: '',
        height_mm: '',
        height_inch: '',
        wall_height_mm: '',
        wall_height_inch: ''
      });
    } else {
      // Validation for local products
      if (!localProduct.product_size || !localProduct.product_type || !localProduct.selling_price || !localProduct.supplier || !localProduct.purchase_price) {
        alert('الرجاء إدخال جميع بيانات المنتج المحلي');
        return;
      }

      const product_name = `${localProduct.product_size} - ${localProduct.product_type}`;

      const item = {
        // للمنتجات المحلية، حقول المنتجات المصنعة يجب أن تكون null
        seal_type: null,
        material_type: null, 
        inner_diameter: null,
        outer_diameter: null,
        height: null,
        product_type: 'local',
        product_name: product_name,
        product_size: localProduct.product_size,
        product_type_name: localProduct.product_type,
        supplier: localProduct.supplier,
        purchase_price: parseFloat(localProduct.purchase_price),
        selling_price: parseFloat(localProduct.selling_price),
        quantity: parseInt(currentItem.quantity),
        unit_price: parseFloat(localProduct.selling_price), // Use selling price as unit price
        total_price: parseFloat(localProduct.selling_price) * parseInt(currentItem.quantity),
        // Store local product details
        local_product_details: {
          product_size: localProduct.product_size,
          product_type: localProduct.product_type,
          supplier: localProduct.supplier,
          purchase_price: parseFloat(localProduct.purchase_price),
          selling_price: parseFloat(localProduct.selling_price)
        }
      };

      setItems([...items, item]);
      setLocalProduct({
        product_size: '',
        product_type: '',
        purchase_price: '',
        selling_price: '',
        supplier: ''
      });
      setCurrentItem({
        seal_type: 'RSL',
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        quantity: 1,
        unit_price: '',
        product_type: 'manufactured'
      });
      setMeasurements({
        inner_diameter_mm: '',
        inner_diameter_inch: '',
        outer_diameter_mm: '',
        outer_diameter_inch: '',
        height_mm: '',
        height_inch: '',
        wall_height_mm: '',
        wall_height_inch: ''
      });
    }
    
    setCompatibilityResults(null);
    setSelectedMaterial(null);
    setSelectedMaterials([]); // مسح الخامات المختارة المتعددة
  };

  const editItem = (index) => {
    const item = items[index];
    
    // Set current item for editing
    setCurrentItem({
      seal_type: item.seal_type || 'RSL',
      material_type: item.material_type || 'NBR',
      inner_diameter: item.inner_diameter?.toString() || '',
      outer_diameter: item.outer_diameter?.toString() || '',
      height: item.height?.toString() || '',
      quantity: item.quantity || 1,
      unit_price: item.unit_price?.toString() || '',
      product_type: item.product_type || (item.local_product_details ? 'local' : 'manufactured')
    });
    
    // Set measurements for dual input fields (assuming values are in mm from database)
    setMeasurements({
      inner_diameter_mm: item.inner_diameter?.toString() || '',
      inner_diameter_inch: mmToInch(item.inner_diameter) || '',
      outer_diameter_mm: item.outer_diameter?.toString() || '',
      outer_diameter_inch: mmToInch(item.outer_diameter) || '',
      height_mm: item.height?.toString() || '',
      height_inch: mmToInch(item.height) || '',
      wall_height_mm: item.wall_height?.toString() || '',
      wall_height_inch: mmToInch(item.wall_height) || ''
    });
    
    // Set wall height if exists
    if (item.wall_height) {
      setWallHeight(item.wall_height.toString());
    }
    
    // Set measurement unit if exists
    if (item.measurement_unit) {
      setMeasurementUnit(item.measurement_unit);
    }
    
    // Set local product details if exists
    if (item.local_product_details) {
      setLocalProduct({
        product_size: item.local_product_details.product_size || '',
        product_type: item.local_product_details.product_type || '',
        purchase_price: '',
        selling_price: item.unit_price?.toString() || '',
        supplier: ''
      });
    }
    
    // Remove the item being edited
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const deleteItem = (index) => {
    if (confirm('هل أنت متأكد من حذف هذا العنصر؟')) {
      const newItems = items.filter((_, i) => i !== index);
      setItems(newItems);
    }
  };

  const [isCreatingInvoice, setIsCreatingInvoice] = useState(false);

  const createInvoice = async () => {
    // منع التكرار أثناء إنشاء الفاتورة
    if (isCreatingInvoice) {
      return;
    }

    if (!selectedCustomer && !newCustomer) {
      alert('الرجاء اختيار العميل أو إدخال اسم عميل جديد');
      return;
    }

    if (items.length === 0) {
      alert('الرجاء إضافة منتجات للفاتورة');
      return;
    }

    try {
      setIsCreatingInvoice(true); // بدء إنشاء الفاتورة
      
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

      // حساب الإجمالي والخصم
      const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
      const discountAmount = discountType === 'percentage' 
        ? (subtotal * parseFloat(discount || 0)) / 100
        : parseFloat(discount || 0);
      const totalAfterDiscount = subtotal - discountAmount;

      // إنشاء الفاتورة
      const invoiceData = {
        customer_id: customerId,
        customer_name: customerName,
        invoice_title: invoiceTitle, // عنوان الفاتورة
        supervisor_name: supervisorName, // اسم المشرف
        items: items,
        payment_method: paymentMethod,
        subtotal: subtotal,
        discount: discountAmount,
        discount_type: discountType,
        discount_value: parseFloat(discount || 0),
        total_after_discount: totalAfterDiscount,
        notes: ''
      };

      const response = await axios.post(`${API}/invoices?supervisor_name=${encodeURIComponent(supervisorName)}`, invoiceData);
      
      if (response.data) {
        alert('تم إنشاء الفاتورة بنجاح');
        
        // مسح البيانات
        setItems([]);
        setSelectedCustomer('');
        setNewCustomer('');
        setSupervisorName('');
        setInvoiceTitle(''); // مسح عنوان الفاتورة
        setPaymentMethod('نقدي');
        setDiscount(0);
        setDiscountType('amount');
        setClientType(1); // إعادة تعيين نوع العميل
        
        // طباعة الفاتورة
        printInvoice(response.data);
      }
    } catch (error) {
      console.error('Error creating invoice:', error);
      alert('حدث خطأ في إنشاء الفاتورة: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsCreatingInvoice(false); // إنهاء حالة الإنشاء
    }
  };

  const printInvoice = (invoice) => {
    const printContent = `
      <!DOCTYPE html>
      <html dir="rtl">
      <head>
        <meta charset="UTF-8">
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            direction: rtl;
            font-size: 15px;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
            margin-bottom: 20px;
          }
          .company-info {
            text-align: right;
          }
          .company-name {
            font-size: 32px;
            font-weight: bold;
            color: #000;
            margin: 0;
          }
          .company-subtitle {
            font-size: 20px;
            margin: 5px 0;
            color: #666;
          }
          .company-details {
            font-size: 16px;
            margin: 2px 0;
            color: #333;
          }
          .logo-section {
            text-align: center;
            flex: 1;
          }
          .invoice-title {
            font-size: 20px;
            font-weight: bold;
            background-color: #ff4444;
            color: white;
            padding: 8px 20px;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 10px;
          }
          .invoice-number {
            font-size: 18px;
            font-weight: bold;
            color: #ff4444;
          }
          .customer-info {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
          }
          .customer-details {
            text-align: right;
          }
          .date-info {
            text-align: left;
          }
          .products-table {
            width: 100%;
            border-collapse: collapse;
            border: 2px solid #000;
            margin: 20px 0;
          }
          .products-table th,
          .products-table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: center;
          }
          .products-table th {
            background-color: #f0f0f0;
            font-weight: bold;
          }
          .footer {
            margin-top: 30px;
            border-top: 1px solid #ccc;
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #666;
          }
          .total-section {
            text-align: left;
            margin-top: 10px;
          }
          .total-amount {
            font-size: 18px;
            font-weight: bold;
            border: 2px solid #000;
            padding: 10px;
            display: inline-block;
            background-color: #f9f9f9;
          }
          @media print {
            body { margin: 0; padding: 10px; }
          }
        </style>
      </head>
      <body>
        <!-- Header Section -->
        <div class="header">
          <div class="company-info">
            <h1 class="company-name">شركة ماستر سيل</h1>
            <p class="company-subtitle">تصنيع جميع أنواع الأويل سيل</p>
            <p class="company-details">جميع الأقطار حتى ٥٠٠مل</p>
            <p class="company-details">هيدروليك - نيوماتيك</p>
          </div>
          
          <div class="logo-section">
            <img src="https://customer-assets.emergentagent.com/job_oilseal-mgmt/artifacts/42i3e7yn_WhatsApp%20Image%202025-07-31%20at%2015.14.10_e8c55120.jpg" 
                 alt="Master Seal Logo" 
                 style="max-width: 120px; max-height: 80px; margin-bottom: 10px;">
            <div class="invoice-title">${invoice.invoice_title || 'عرض سعر'}</div>
            <div class="invoice-number">${invoice.invoice_number}</div>
          </div>
        </div>

        <!-- Customer and Date Info -->
        <div class="customer-info">
          <div class="customer-details">
            <p><strong>السادة:</strong> ${invoice.customer_name}</p>
            <p><strong>العنوان:</strong> ${invoice.customer_address || '........................'}</p>
          </div>
          <div class="date-info">
            <p><strong>تحرير في:</strong> ${new Date(invoice.date).toLocaleDateString('ar-EG')}</p>
            <p><strong>Date:</strong> ${new Date(invoice.date).toLocaleDateString('en-GB')}</p>
          </div>
        </div>

        <!-- Products Table -->
        <table class="products-table">
          <thead>
            <tr>
              <th style="width: 60px;">المسلسل<br>Item</th>
              <th style="width: 80px;">الكمية<br>QTY</th>
              <th style="width: 200px;">Description<br>المواصفات</th>
              <th style="width: 100px;">سعر الوحدة<br>Unit Price</th>
              <th style="width: 100px;">إجمالي<br>Total</th>
            </tr>
          </thead>
          <tbody>
            ${invoice.items.map((item, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>${item.quantity}</td>
                <td style="text-align: right;">
                  ${item.local_product_details ? 
                    `${item.local_product_details.product_size} - ${item.local_product_details.product_type}` : 
                    `${item.seal_type} - ${item.material_type}<br>
                    <small>${item.inner_diameter} × ${item.outer_diameter} × ${item.height} مم${item.wall_height ? ` (ارتفاع الحيطة: ${item.wall_height} مم)` : ""}</small>`
                  }
                </td>
                <td>ج.م ${item.unit_price.toFixed(2)}</td>
                <td>ج.م ${item.total_price.toFixed(2)}</td>
              </tr>
            `).join('')}
            <!-- Empty rows for additional items -->
            ${Array.from({length: Math.max(0, 8 - invoice.items.length)}, (_, i) => `
              <tr style="height: 40px;">
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <!-- Total Section -->
        <div class="total-section">
          <div style="text-align: left; margin-bottom: 10px;">
            ${invoice.subtotal ? `
              <div style="margin-bottom: 5px;">
                <span>المجموع الفرعي: ج.م ${invoice.subtotal.toFixed(2)}</span>
              </div>
            ` : ''}
            ${invoice.discount && invoice.discount > 0 ? `
              <div style="margin-bottom: 5px; color: #d32f2f;">
                <span>الخصم: - ج.م ${invoice.discount.toFixed(2)}</span>
                ${invoice.discount_type === 'percentage' && invoice.discount_value ? 
                  ` <small>(${invoice.discount_value}%)</small>` : ''}
              </div>
              <hr style="margin: 5px 0; border: 1px solid #000;">
            ` : ''}
          </div>
          <div class="total-amount">
            الإجمالي النهائي: ج.م ${(invoice.total_after_discount || invoice.total_amount).toFixed(2)}
          </div>
        </div>

        <!-- Additional Info -->
        <div style="margin-top: 20px; text-align: center; font-size: 12px;">
          <p><strong>ملحوظة:</strong> فقط وقدره</p>
          <div style="height: 30px; border-bottom: 1px solid #000; margin: 10px 40px;"></div>
        </div>

        <!-- Footer -->
        <div class="footer">
          <div>
            <p><strong>التوقيع:</strong></p>
            <p>موبايل: ٠١٠٢٠٦٣٠٦٧٧ - ٠١٠٦٢٣٩٠٨٧٠</p>
            <p>تليفون: ٠١٠٢٠٦٣٠٦٧٧</p>
          </div>
          <div style="text-align: left;">
            <p><strong>المستلم:</strong></p>
            <p>الحرفيين - السلام - أمام السوبر جيت</p>
            <p>موبايل: ٠١٠٢٠٦٣٠٦٧٧ - ٠١٠٦٢٣٩٠٨٧٠</p>
          </div>
        </div>

        <!-- Note -->
        <div style="text-align: center; margin-top: 20px; font-size: 11px; color: #666;">
          <p>يقر المشتري بأنه قام بمعاينة البضاعة وقبولها</p>
        </div>
      </body>
      </html>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  const clearAllInvoices = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع العناصر؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    try {
      setItems([]);
      alert('تم حذف جميع العناصر');
    } catch (error) {
      alert('حدث خطأ في حذف البيانات');
    }
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
            
            <div>
              <label className="block text-sm font-medium mb-1">اسم المشرف على التصنيع</label>
              <input
                type="text"
                value={supervisorName}
                onChange={(e) => setSupervisorName(e.target.value)}
                placeholder="اسم المشرف (اختياري)"
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">عنوان الفاتورة</label>
              <input
                type="text"
                value={invoiceTitle}
                onChange={(e) => setInvoiceTitle(e.target.value)}
                placeholder="عنوان الفاتورة (اختياري)"
                className="w-full p-2 border border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Product Entry */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">إضافة منتج</h3>
          
          {/* Product Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">نوع المنتج</label>
            <select
              value={currentItem.product_type}
              onChange={(e) => setCurrentItem({...currentItem, product_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              <option value="manufactured">منتج تصنيع</option>
              <option value="local">منتج محلي</option>
            </select>
          </div>
          
          {/* Conditional Product Forms */}
          {currentItem.product_type === 'manufactured' ? (
            // Manufacturing Product Form
            <>
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
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">مليمتر</label>
                      <input
                        type="number"
                        step="0.01"
                        value={measurements.inner_diameter_mm}
                        onChange={(e) => handleMeasurementChange('inner_diameter', e.target.value, 'mm')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="مم"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">بوصة</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={measurements.inner_diameter_inch}
                        onChange={(e) => handleMeasurementChange('inner_diameter', e.target.value, 'inch')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="بوصة"
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">القطر الخارجي</label>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">مليمتر</label>
                      <input
                        type="number"
                        step="0.01"
                        value={measurements.outer_diameter_mm}
                        onChange={(e) => handleMeasurementChange('outer_diameter', e.target.value, 'mm')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="مم"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">بوصة</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={measurements.outer_diameter_inch}
                        onChange={(e) => handleMeasurementChange('outer_diameter', e.target.value, 'inch')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="بوصة"
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">ارتفاع السيل</label>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">مليمتر</label>
                      <input
                        type="number"
                        step="0.01"
                        value={measurements.height_mm}
                        onChange={(e) => handleMeasurementChange('height', e.target.value, 'mm')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="مم"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">بوصة</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={measurements.height_inch}
                        onChange={(e) => handleMeasurementChange('height', e.target.value, 'inch')}
                        className="w-full p-2 border border-gray-300 rounded text-sm"
                        placeholder="بوصة"
                      />
                    </div>
                  </div>
                </div>
                
                {/* Wall Height for W-type seals */}
                {currentItem.seal_type && currentItem.seal_type.startsWith('W') && (
                  <div>
                    <label className="block text-sm font-medium mb-1">ارتفاع الحيطة</label>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">مليمتر</label>
                        <input
                          type="number"
                          step="0.01"
                          value={measurements.wall_height_mm}
                          onChange={(e) => handleMeasurementChange('wall_height', e.target.value, 'mm')}
                          className="w-full p-2 border border-gray-300 rounded text-sm"
                          placeholder="ارتفاع الحيطة بالمليمتر"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">بوصة</label>
                        <input
                          type="number"
                          step="0.0001"
                          value={measurements.wall_height_inch}
                          onChange={(e) => handleMeasurementChange('wall_height', e.target.value, 'inch')}
                          className="w-full p-2 border border-gray-300 rounded text-sm"
                          placeholder="ارتفاع الحيطة بالبوصة"
                        />
                      </div>
                    </div>
                  </div>
                )}
                
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
                  <label className="block text-sm font-medium mb-1">نوع العميل للتسعير</label>
                  <select
                    value={clientType}
                    onChange={(e) => setClientType(parseInt(e.target.value))}
                    className="w-full p-2 border border-gray-300 rounded"
                  >
                    <option value={1}>عميل 1</option>
                    <option value={2}>عميل 2</option>
                    <option value={3}>عميل 3</option>
                  </select>
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
                
                <div>
                  <label className="block text-sm font-medium mb-1">ملاحظات</label>
                  <textarea
                    value={currentItem.notes || ''}
                    onChange={(e) => setCurrentItem({...currentItem, notes: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    rows="2"
                    placeholder="ملاحظات إضافية..."
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
            </>
          ) : (
            // Local Product Form
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">مقاس المنتج</label>
                  <input
                    type="text"
                    value={localProduct.product_size}
                    onChange={(e) => setLocalProduct({...localProduct, product_size: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="مقاس المنتج"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">نوع المنتج</label>
                  <input
                    type="text"
                    value={localProduct.product_type}
                    onChange={(e) => setLocalProduct({...localProduct, product_type: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="نوع المنتج"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">المورد</label>
                  <input
                    type="text"
                    value={localProduct.supplier}
                    onChange={(e) => setLocalProduct({...localProduct, supplier: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="اسم المورد"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">سعر الشراء</label>
                  <input
                    type="number"
                    step="0.01"
                    value={localProduct.purchase_price}
                    onChange={(e) => setLocalProduct({...localProduct, purchase_price: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="سعر الشراء"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">سعر البيع</label>
                  <input
                    type="number"
                    step="0.01"
                    value={localProduct.selling_price}
                    onChange={(e) => setLocalProduct({...localProduct, selling_price: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="سعر البيع"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">الكمية</label>
                  <input
                    type="number"
                    value={currentItem.quantity}
                    onChange={(e) => setCurrentItem({...currentItem, quantity: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded"
                  />
                </div>
              </div>
            </>
          )}
          
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
              <h4 className="font-medium mb-2">📦 نتائج فحص التوافق</h4>
              <p className="text-sm text-gray-600 mb-2">اختر الخامات وحدد عدد السيلات من كل خامة (المطلوب: {currentItem.quantity} سيل)</p>
              
              {/* عرض الخامات المختارة */}
              {selectedMaterials.length > 0 && (
                <div className="mb-4 p-3 bg-blue-50 rounded border">
                  <h5 className="font-medium text-blue-800 mb-2">الخامات المختارة:</h5>
                  <div className="space-y-2">
                    {selectedMaterials.map((selected, index) => (
                      <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                        <span className="text-sm">
                          {selected.material.unit_code} - {selected.material.material_type} 
                          {selected.material.inner_diameter}×{selected.material.outer_diameter}×{selected.material.height}
                        </span>
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <input
                            type="number"
                            min="1"
                            max={Math.floor(selected.material.height / (parseFloat(currentItem.height) + 2))}
                            value={selected.seals}
                            onChange={(e) => {
                              const newSelected = [...selectedMaterials];
                              newSelected[index].seals = parseInt(e.target.value) || 0;
                              setSelectedMaterials(newSelected);
                            }}
                            className="w-16 p-1 border rounded text-center"
                          />
                          <span className="text-xs">سيل</span>
                          <button
                            onClick={() => {
                              const newSelected = selectedMaterials.filter((_, i) => i !== index);
                              setSelectedMaterials(newSelected);
                            }}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 text-sm">
                    <span className="font-medium">
                      المجموع: {selectedMaterials.reduce((sum, sel) => sum + sel.seals, 0)} / {currentItem.quantity} سيل
                    </span>
                    {selectedMaterials.reduce((sum, sel) => sum + sel.seals, 0) === parseInt(currentItem.quantity) && (
                      <span className="text-green-600 ml-2">✓ مكتمل</span>
                    )}
                  </div>
                </div>
              )}
              
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {compatibilityResults.compatible_materials.map((material, index) => {
                  const isSelected = selectedMaterials.some(sel => 
                    sel.material.unit_code === material.unit_code && 
                    sel.material.inner_diameter === material.inner_diameter &&
                    sel.material.outer_diameter === material.outer_diameter
                  );
                  const maxSeals = Math.floor(material.height / (parseFloat(currentItem.height) + 2));
                  const remainingSeals = parseInt(currentItem.quantity) - selectedMaterials.reduce((sum, sel) => sum + sel.seals, 0);
                  
                  return (
                    <div key={index} 
                         className={`p-3 rounded border transition-colors ${
                           isSelected ? 'bg-blue-100 border-blue-300' : 'bg-gray-50 hover:bg-gray-100'
                         }`}>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-blue-600">
                            {material.unit_code} - {material.material_type}
                          </p>
                          <p className="text-sm text-gray-600">
                            الأبعاد: {material.inner_diameter} × {material.outer_diameter} × {material.height} مم
                          </p>
                          <p className="text-xs text-green-600">
                            يمكن إنتاج: {maxSeals} سيل كحد أقصى
                          </p>
                          {material.score && (
                            <p className="text-xs text-gray-500">نسبة التوافق: {material.score}%</p>
                          )}
                        </div>
                        {!isSelected && remainingSeals > 0 && maxSeals > 0 && (
                          <button
                            onClick={() => {
                              const newSelection = {
                                material: material,
                                seals: Math.min(maxSeals, remainingSeals)
                              };
                              setSelectedMaterials([...selectedMaterials, newSelection]);
                            }}
                            className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            اختيار
                          </button>
                        )}
                        {isSelected && (
                          <div className="text-blue-600 text-sm font-medium">
                            ✓ مختارة
                          </div>
                        )}
                        {!isSelected && remainingSeals <= 0 && (
                          <div className="text-gray-400 text-sm">
                            مكتمل
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* زر تأكيد الاختيار */}
              {selectedMaterials.length > 0 && (
                <div className="mt-4 flex space-x-2 space-x-reverse">
                  <button
                    onClick={() => {
                      const totalSeals = selectedMaterials.reduce((sum, sel) => sum + sel.seals, 0);
                      if (totalSeals !== parseInt(currentItem.quantity)) {
                        alert(`⚠️ مجموع السيلات المختارة (${totalSeals}) لا يساوي العدد المطلوب (${currentItem.quantity})`);
                        return;
                      }
                      
                      // تأكيد الاختيار وحساب السعر
                      confirmMultiMaterialSelection();
                    }}
                    className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                    disabled={selectedMaterials.reduce((sum, sel) => sum + sel.seals, 0) !== parseInt(currentItem.quantity)}
                  >
                    تأكيد الاختيار
                  </button>
                  <button
                    onClick={() => {
                      setSelectedMaterials([]);
                    }}
                    className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                  >
                    إلغاء الاختيار
                  </button>
                </div>
              )}
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
                      seal_type: product.seal_type,
                      inner_diameter: product.inner_diameter,
                      outer_diameter: product.outer_diameter,
                      height: product.height,
                      is_finished_product: true
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
                  <th className="border border-gray-300 p-2">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={index}>
                    <td className="border border-gray-300 p-2">
                      {item.local_product_details ? item.local_product_details.product_type : item.seal_type}
                    </td>
                    <td className="border border-gray-300 p-2">
                      {item.local_product_details ? 'محلي' : item.material_type}
                    </td>
                    <td className="border border-gray-300 p-2">
                      {item.local_product_details ? 
                        `${item.local_product_details.product_size} - ${item.local_product_details.product_type}` :
                        `${item.original_inner_diameter || item.inner_diameter} × ${item.original_outer_diameter || item.outer_diameter} × ${item.original_height || item.height}${item.original_wall_height ? ` (ارتفاع الحيطة: ${item.original_wall_height})` : (item.wall_height ? ` (ارتفاع الحيطة: ${item.wall_height})` : '')} ${item.measurement_unit || 'مم'}`
                      }
                    </td>
                    <td className="border border-gray-300 p-2">{item.quantity}</td>
                    <td className="border border-gray-300 p-2">ج.م {item.unit_price}</td>
                    <td className="border border-gray-300 p-2">ج.م {item.total_price}</td>
                    <td className="border border-gray-300 p-2">
                      <div className="flex space-x-2 space-x-reverse">
                        <button
                          onClick={() => editItem(index)}
                          className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          title="تحرير"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => deleteItem(index)}
                          className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          title="حذف"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
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
                <option value="يد الصاوي">يد الصاوي</option>
              </select>
            </div>
            
            {/* Discount Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium mb-1">نوع الخصم</label>
                <select
                  value={discountType}
                  onChange={(e) => setDiscountType(e.target.value)}
                  className="p-2 border border-gray-300 rounded w-full"
                >
                  <option value="amount">مبلغ ثابت</option>
                  <option value="percentage">نسبة مئوية</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">
                  قيمة الخصم {discountType === 'percentage' ? '(%)' : '(ج.م)'}
                </label>
                <input
                  type="number"
                  value={discount}
                  onChange={(e) => setDiscount(e.target.value)}
                  className="p-2 border border-gray-300 rounded w-full"
                  placeholder="0"
                  min="0"
                  step={discountType === 'percentage' ? '0.1' : '0.01'}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">مبلغ الخصم</label>
                <div className="p-2 bg-white border border-gray-300 rounded w-full">
                  ج.م {(() => {
                    const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
                    const discountAmount = discountType === 'percentage' 
                      ? (subtotal * parseFloat(discount || 0)) / 100
                      : parseFloat(discount || 0);
                    return discountAmount.toFixed(2);
                  })()}
                </div>
              </div>
            </div>
            
            {/* Total Section */}
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-lg">المجموع الفرعي:</span>
                <span className="text-lg font-semibold">
                  ج.م {items.reduce((sum, item) => sum + item.total_price, 0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-lg">الخصم:</span>
                <span className="text-lg font-semibold text-red-600">
                  - ج.م {(() => {
                    const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
                    const discountAmount = discountType === 'percentage' 
                      ? (subtotal * parseFloat(discount || 0)) / 100
                      : parseFloat(discount || 0);
                    return discountAmount.toFixed(2);
                  })()}
                </span>
              </div>
              <hr className="my-2" />
              <div className="flex justify-between items-center">
                <span className="text-xl font-bold">الإجمالي النهائي:</span>
                <span className="text-xl font-bold text-green-600">
                  ج.م {(() => {
                    const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
                    const discountAmount = discountType === 'percentage' 
                      ? (subtotal * parseFloat(discount || 0)) / 100
                      : parseFloat(discount || 0);
                    return (subtotal - discountAmount).toFixed(2);
                  })()}
                </span>
              </div>
            </div>
            
            <div className="text-xl font-bold" style={{display: 'none'}}>
              الإجمالي: ج.م {items.reduce((sum, item) => sum + item.total_price, 0).toFixed(2)}
            </div>
          </div>
          
          <button
            onClick={createInvoice}
            disabled={isCreatingInvoice}
            className={`w-full p-3 rounded mt-4 text-lg font-semibold ${
              isCreatingInvoice 
                ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {isCreatingInvoice ? 'جاري إنشاء الفاتورة...' : 'إنشاء الفاتورة'}
          </button>
        </div>
      )}
    </div>
  );
};

// Simple placeholder components for other pages
// Inventory Component will be replaced with new advanced version above

// Stock Component (Old Inventory functionality for Raw Materials and Finished Products)
const Stock = () => {
  const [rawMaterials, setRawMaterials] = useState([]);
  const [finishedProducts, setFinishedProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState(''); // للبحث
  const [newRawMaterial, setNewRawMaterial] = useState({
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    height: '',
    pieces_count: '',
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
  const sealTypes = ['RSL', 'RS', 'RSS', 'RSE', 'B17', 'B3', 'B14', 'B1', 'R15', 'R17', 'W1', 'W4', 'W5', 'W11', 'WBT', 'XR', 'CH', 'VR'];

  // دالة تصفية البحث
  const filteredRawMaterials = rawMaterials.filter(material => 
    material.material_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    material.unit_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    material.inner_diameter.toString().includes(searchTerm) ||
    material.outer_diameter.toString().includes(searchTerm) ||
    material.height.toString().includes(searchTerm)
  ).sort((a, b) => {
    // ترتيب حسب أولوية الخامة: BUR-NBR-BT-BOOM-VT
    const materialPriority = { 'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5 };
    const aPriority = materialPriority[a.material_type] || 6;
    const bPriority = materialPriority[b.material_type] || 6;
    
    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }
    // ثم ترتيب حسب المقاس (القطر الداخلي ثم الخارجي)
    if (a.inner_diameter !== b.inner_diameter) {
      return a.inner_diameter - b.inner_diameter;
    }
    return a.outer_diameter - b.outer_diameter;
  });

  const filteredFinishedProducts = finishedProducts.filter(product => 
    product.seal_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.material_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.inner_diameter.toString().includes(searchTerm) ||
    product.outer_diameter.toString().includes(searchTerm) ||
    product.height.toString().includes(searchTerm)
  ).sort((a, b) => {
    // ترتيب حسب أولوية الخامة: BUR-NBR-BT-BOOM-VT
    const materialPriority = { 'BUR': 1, 'NBR': 2, 'BT': 3, 'BOOM': 4, 'VT': 5 };
    const aPriority = materialPriority[a.material_type] || 6;
    const bPriority = materialPriority[b.material_type] || 6;
    
    if (aPriority !== bPriority) {
      return aPriority - bPriority;
    }
    // ثم ترتيب حسب المقاس (القطر الداخلي ثم الخارجي)
    if (a.inner_diameter !== b.inner_diameter) {
      return a.inner_diameter - b.inner_diameter;
    }
    return a.outer_diameter - b.outer_diameter;
  });

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
    if (!newRawMaterial.inner_diameter || !newRawMaterial.outer_diameter || !newRawMaterial.height || !newRawMaterial.pieces_count || !newRawMaterial.cost_per_mm) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      const rawMaterial = {
        material_type: newRawMaterial.material_type,
        inner_diameter: parseFloat(newRawMaterial.inner_diameter),
        outer_diameter: parseFloat(newRawMaterial.outer_diameter),
        height: parseFloat(newRawMaterial.height),
        pieces_count: parseInt(newRawMaterial.pieces_count),
        cost_per_mm: parseFloat(newRawMaterial.cost_per_mm)
        // unit_code will be generated automatically by backend
      };

      let response;
      if (newRawMaterial.id) {
        // Update existing material
        response = await axios.put(`${API}/raw-materials/${newRawMaterial.id}`, rawMaterial);
        alert(`تم تحديث المادة الخام بنجاح. كود الوحدة: ${response.data.unit_code}`);
      } else {
        // Add new material
        response = await axios.post(`${API}/raw-materials`, rawMaterial);
        alert(`تم إضافة المادة الخام بنجاح. كود الوحدة: ${response.data.unit_code}`);
      }

      fetchRawMaterials();
      setNewRawMaterial({
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        pieces_count: '',
        cost_per_mm: ''
      });
    } catch (error) {
      console.error('Error saving raw material:', error);
      alert('حدث خطأ في حفظ المادة الخام: ' + (error.response?.data?.detail || error.message));
    }
  };

  const clearAllRawMaterials = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع المواد الخام؟')) {
      return;
    }

    try {
      await axios.delete(`${API}/raw-materials/clear-all`);
      fetchRawMaterials();
      alert('تم حذف جميع المواد الخام');
    } catch (error) {
      console.error('Error clearing raw materials:', error);
      alert('حدث خطأ في حذف المواد الخام');
    }
  };

  const deleteRawMaterial = async (materialId) => {
    if (!confirm('هل أنت متأكد من حذف هذه المادة الخام؟')) {
      return;
    }

    try {
      await axios.delete(`${API}/raw-materials/${materialId}`);
      fetchRawMaterials();
      alert('تم حذف المادة الخام');
    } catch (error) {
      console.error('Error deleting raw material:', error);
      alert('حدث خطأ في حذف المادة الخام');
    }
  };

  const editRawMaterial = (material) => {
    // Fill the form with the material data for editing
    setNewRawMaterial({
      id: material.id,
      material_type: material.material_type,
      inner_diameter: material.inner_diameter.toString(),
      outer_diameter: material.outer_diameter.toString(),
      height: material.height.toString(),
      pieces_count: material.pieces_count.toString(),
      cost_per_mm: material.cost_per_mm.toString()
    });
  };

  const handleFileImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/excel/import/raw-materials`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      alert(response.data.message);
      fetchRawMaterials(); // Refresh the raw materials list
      event.target.value = ''; // Clear file input
    } catch (error) {
      console.error('Error importing file:', error);
      alert('حدث خطأ في استيراد الملف: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleFileExport = async () => {
    try {
      const response = await axios.get(`${API}/excel/export/raw-materials`, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `raw_materials_export_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting file:', error);
      alert('حدث خطأ في تصدير الملف');
    }
  };

  const addFinishedProduct = async () => {
    if (!newFinishedProduct.inner_diameter || !newFinishedProduct.outer_diameter || !newFinishedProduct.height || !newFinishedProduct.quantity || !newFinishedProduct.unit_price) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      const finishedProduct = {
        seal_type: newFinishedProduct.seal_type,
        material_type: newFinishedProduct.material_type,
        inner_diameter: parseFloat(newFinishedProduct.inner_diameter),
        outer_diameter: parseFloat(newFinishedProduct.outer_diameter),
        height: parseFloat(newFinishedProduct.height),
        quantity: parseInt(newFinishedProduct.quantity),
        unit_price: parseFloat(newFinishedProduct.unit_price)
      };

      if (newFinishedProduct.id) {
        // Update existing product
        await axios.put(`${API}/finished-products/${newFinishedProduct.id}`, finishedProduct);
        alert('تم تحديث المنتج النهائي بنجاح');
      } else {
        // Add new product
        await axios.post(`${API}/finished-products`, finishedProduct);
        alert('تم إضافة المنتج النهائي بنجاح');
      }

      fetchFinishedProducts();
      setNewFinishedProduct({
        seal_type: 'RSL',
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        height: '',
        quantity: '',
        unit_price: ''
      });
    } catch (error) {
      console.error('Error saving finished product:', error);
      alert('حدث خطأ في حفظ المنتج النهائي');
    }
  };

  const editFinishedProduct = (product) => {
    // Fill the form with the product data for editing
    setNewFinishedProduct({
      id: product.id,
      seal_type: product.seal_type,
      material_type: product.material_type,
      inner_diameter: product.inner_diameter.toString(),
      outer_diameter: product.outer_diameter.toString(),
      height: product.height.toString(),
      quantity: product.quantity.toString(),
      unit_price: product.unit_price.toString()
    });
  };

  const deleteFinishedProduct = async (productId) => {
    if (!confirm('هل أنت متأكد من حذف هذا المنتج النهائي؟')) {
      return;
    }

    try {
      await axios.delete(`${API}/finished-products/${productId}`);
      fetchFinishedProducts();
      alert('تم حذف المنتج النهائي');
    } catch (error) {
      console.error('Error deleting finished product:', error);
      alert('حدث خطأ في حذف المنتج النهائي');
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <h1 className="text-3xl font-bold mb-6">إدارة المخزون</h1>
      
      {/* Raw Materials Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">مخزون المواد الخام</h3>
          <div className="flex space-x-2 space-x-reverse">
            <button
              onClick={clearAllRawMaterials}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              حذف الكل
            </button>
          </div>
        </div>

        {/* Import/Export Section */}
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h4 className="font-medium mb-4">📁 استيراد وتصدير المواد الخام</h4>
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <label className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 cursor-pointer">
                📤 استيراد من Excel
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileImport}
                  className="hidden"
                />
              </label>
              <span className="text-sm text-gray-600">(.xlsx أو .xls)</span>
            </div>
            
            <button
              onClick={handleFileExport}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              📥 تصدير إلى Excel
            </button>
            
            <div className="text-sm text-gray-600 bg-white p-2 rounded border">
              <strong>تنسيق الملف المطلوب:</strong><br/>
              material_type, inner_diameter, outer_diameter, height, pieces_count, unit_code, cost_per_mm
            </div>
          </div>
        </div>
        
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
            <label className="block text-sm font-medium mb-1">الارتفاع (مم)</label>
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
            <label className="block text-sm font-medium mb-1">تكلفة المللي</label>
            <input
              type="number"
              step="0.01"
              value={newRawMaterial.cost_per_mm}
              onChange={(e) => setNewRawMaterial({...newRawMaterial, cost_per_mm: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        </div>
        
        <p className="text-sm text-gray-600 mt-4">
          ملاحظة: سيتم توليد كود الوحدة تلقائياً حسب نوع الخامة والمواصفات
        </p>
        
        <button
          onClick={addRawMaterial}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4"
        >
          إضافة مادة خام
        </button>

        {/* حقل البحث */}
        <div className="mb-4">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="بحث في المواد الخام (نوع الخامة، كود الوحدة، المقاسات...)"
            className="w-full p-3 border border-gray-300 rounded-lg"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">نوع الخامة</th>
                <th className="border border-gray-300 p-2">القطر الداخلي</th>
                <th className="border border-gray-300 p-2">القطر الخارجي</th>
                <th className="border border-gray-300 p-2">الارتفاع</th>
                <th className="border border-gray-300 p-2">عدد القطع</th>
                <th className="border border-gray-300 p-2">كود الوحدة</th>
                <th className="border border-gray-300 p-2">تكلفة المللي</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {filteredRawMaterials.map(material => (
                <tr key={material.id}>
                  <td className="border border-gray-300 p-2">{material.material_type}</td>
                  <td className="border border-gray-300 p-2">{material.inner_diameter}</td>
                  <td className="border border-gray-300 p-2">{material.outer_diameter}</td>
                  <td className="border border-gray-300 p-2">{material.height}</td>
                  <td className="border border-gray-300 p-2">{material.pieces_count}</td>
                  <td className="border border-gray-300 p-2">{material.unit_code}</td>
                  <td className="border border-gray-300 p-2">{material.cost_per_mm}</td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button
                        onClick={() => editRawMaterial(material)}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                        title="تحرير"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => deleteRawMaterial(material.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                        title="حذف"
                      >
                        🗑️
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
            <label className="block text-sm font-medium mb-1">ارتفاع السيل</label>
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
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mb-4"
        >
          إضافة منتج نهائي
        </button>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 p-2">نوع السيل</th>
                <th className="border border-gray-300 p-2">نوع الخامة</th>
                <th className="border border-gray-300 p-2">القطر الداخلي</th>
                <th className="border border-gray-300 p-2">القطر الخارجي</th>
                <th className="border border-gray-300 p-2">الارتفاع</th>
                <th className="border border-gray-300 p-2">الكمية</th>
                <th className="border border-gray-300 p-2">سعر الوحدة</th>
                <th className="border border-gray-300 p-2">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {filteredFinishedProducts.map(product => (
                <tr key={product.id}>
                  <td className="border border-gray-300 p-2">{product.seal_type}</td>
                  <td className="border border-gray-300 p-2">{product.material_type}</td>
                  <td className="border border-gray-300 p-2">{product.inner_diameter}</td>
                  <td className="border border-gray-300 p-2">{product.outer_diameter}</td>
                  <td className="border border-gray-300 p-2">{product.height}</td>
                  <td className="border border-gray-300 p-2">{product.quantity}</td>
                  <td className="border border-gray-300 p-2">{product.unit_price}</td>
                  <td className="border border-gray-300 p-2">
                    <div className="flex space-x-2 space-x-reverse">
                      <button
                        onClick={() => editFinishedProduct(product)}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                        title="تحرير"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => deleteFinishedProduct(product.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                        title="حذف"
                      >
                        🗑️
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
  const { user } = useAuth();
  const [unpaidInvoices, setUnpaidInvoices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('نقدي');
  const [paymentNotes, setPaymentNotes] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // إجماليات لكل عميل
  const [customerTotals, setCustomerTotals] = useState({});

  useEffect(() => {
    fetchUnpaidInvoices();
    fetchCustomers();
  }, []);

  useEffect(() => {
    // حساب إجماليات العملاء
    const totals = {};
    filteredInvoices.forEach(invoice => {
      const customerName = invoice.customer_name;
      if (!totals[customerName]) {
        totals[customerName] = {
          totalAmount: 0,
          invoiceCount: 0
        };
      }
      totals[customerName].totalAmount += invoice.remaining_amount || invoice.total_amount;
      totals[customerName].invoiceCount += 1;
    });
    setCustomerTotals(totals);
  }, [unpaidInvoices, searchTerm]);
  
  // فلترة الفواتير حسب البحث
  const filteredInvoices = unpaidInvoices.filter(invoice => 
    invoice.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (invoice.invoice_title && invoice.invoice_title.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  useEffect(() => {
    fetchUnpaidInvoices();
    fetchCustomers();
  }, []);

  const fetchUnpaidInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      const invoices = response.data.filter(invoice => 
        // يجب أن تكون الفاتورة آجلة أو لها مبلغ مستحق
        (invoice.payment_method === 'آجل' || invoice.remaining_amount > 0) &&
        (invoice.status === 'غير مدفوعة' || 
         invoice.status === 'مدفوعة جزئياً' || 
         invoice.status === 'انتظار' ||
         invoice.remaining_amount > 0)
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
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-blue-600 mb-2 md:mb-0">الآجل - متابعة المدفوعات</h3>
          <div className="flex space-x-2 space-x-reverse">
            <button 
              onClick={() => window.print()} 
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
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
        
        {/* شريط البحث وإجماليات العملاء */}
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <div className="mb-3">
            <input
              type="text"
              placeholder="بحث بالعميل أو رقم الفاتورة أو العنوان..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
          
          {/* عرض إجماليات العملاء */}
          {Object.keys(customerTotals).length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {Object.entries(customerTotals).map(([customerName, totals]) => (
                <div key={customerName} className="bg-white p-3 rounded border text-center">
                  <div className="font-semibold text-blue-800 text-sm">{customerName}</div>
                  <div className="text-xs text-blue-600">
                    {totals.invoiceCount} فاتورة
                  </div>
                  <div className="text-sm font-bold text-green-600">
                    {totals.totalAmount.toFixed(2)} ج.م
                  </div>
                </div>
              ))}
            </div>
          )}
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
              {filteredInvoices.map((invoice) => (
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
                      <select
                        value={invoice.payment_method}
                        onChange={async (e) => {
                          if (confirm(`هل تريد تحويل طريقة الدفع من "${invoice.payment_method}" إلى "${e.target.value}"؟`)) {
                            try {
                              await axios.put(`${API}/invoices/${invoice.id}/change-payment-method`, null, {
                                params: {
                                  new_payment_method: e.target.value,
                                  username: user?.username
                                }
                              });
                              alert('تم تحويل طريقة الدفع بنجاح');
                              fetchUnpaidInvoices();
                            } catch (error) {
                              alert('خطأ في تحويل طريقة الدفع: ' + (error.response?.data?.detail || error.message));
                            }
                          }
                        }}
                        className="text-xs border rounded px-2 py-1"
                      >
                        <option value="نقدي">نقدي</option>
                        <option value="فودافون كاش محمد الصاوي">فودافون الصاوي</option>
                        <option value="فودافون كاش وائل محمد">فودافون وائل</option>
                        <option value="انستاباي">انستاباي</option>
                        <option value="يد الصاوي">يد الصاوي</option>
                        <option value="آجل">آجل</option>
                      </select>
                      {user?.username === 'Elsawy' && (
                        <button 
                          onClick={async () => {
                            if (confirm(`⚠️ هل أنت متأكد من إلغاء الفاتورة ${invoice.invoice_number}؟ سيتم استرداد المواد وعكس المعاملات المالية.`)) {
                              try {
                                await axios.delete(`${API}/invoices/${invoice.id}/cancel`, {
                                  params: { username: user?.username }
                                });
                                alert('تم إلغاء الفاتورة بنجاح');
                                fetchUnpaidInvoices();
                              } catch (error) {
                                alert('خطأ في إلغاء الفاتورة: ' + (error.response?.data?.detail || error.message));
                              }
                            }
                          }}
                          className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600">
                          إلغاء
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
              لا توجد فواتير غير مسددة
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-red-50 p-4 rounded">
            <h4 className="font-semibold text-red-800">إجمالي المبالغ المستحقة</h4>
            <p className="text-2xl font-bold text-red-600">
              ج.م {filteredInvoices.reduce((sum, inv) => sum + (inv.remaining_amount || 0), 0).toFixed(2)}
            </p>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded">
            <h4 className="font-semibold text-yellow-800">عدد الفواتير المعلقة</h4>
            <p className="text-2xl font-bold text-yellow-600">{filteredInvoices.length}</p>
          </div>
          
          <div className="bg-blue-50 p-4 rounded">
            <h4 className="font-semibold text-blue-800">إجمالي المبلغ الأصلي</h4>
            <p className="text-2xl font-bold text-blue-600">
              ج.م {filteredInvoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0).toFixed(2)}
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

  const clearAllExpenses = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع المصروفات؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    try {
      await axios.delete(`${API}/expenses/clear-all`);
      fetchExpenses();
      alert('تم حذف جميع المصروفات');
    } catch (error) {
      console.error('Error clearing expenses:', error);
      alert('حدث خطأ في حذف البيانات');
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">المصروفات</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button 
            onClick={clearAllExpenses}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
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
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [editForm, setEditForm] = useState({
    invoice_title: '',
    supervisor_name: '',
    customer_name: '',
    payment_method: 'نقدي',
    discount_type: 'amount',
    discount_value: 0,
    items: [],
    notes: ''
  });

  // Payment method conversion state
  const [showPaymentMethodModal, setShowPaymentMethodModal] = useState(false);
  const [selectedInvoiceForPayment, setSelectedInvoiceForPayment] = useState(null);
  const [newPaymentMethod, setNewPaymentMethod] = useState('نقدي');

  // Invoice cancellation state
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedInvoiceForCancel, setSelectedInvoiceForCancel] = useState(null);

  useEffect(() => {
    fetchInvoices();
    fetchCustomers();
  }, []);

  const fetchInvoices = async () => {
    try {
      console.log('Fetching invoices...');
      const response = await axios.get(`${API}/invoices`);
      console.log('Invoices fetched:', response.data.length, 'invoices');
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      alert('خطأ في تحميل الفواتير: ' + (error.response?.data?.detail || error.message));
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

  const startEditInvoice = (invoice) => {
    setEditingInvoice(invoice.id);
    setEditForm({
      invoice_title: invoice.invoice_title || '',
      supervisor_name: invoice.supervisor_name || '',
      customer_name: invoice.customer_name || '',
      payment_method: invoice.payment_method || 'نقدي',
      discount_type: invoice.discount_type || 'amount',
      discount_value: invoice.discount_value || 0,
      items: invoice.items || [],
      notes: invoice.notes || ''
    });
  };

  const cancelEdit = () => {
    setEditingInvoice(null);
    setEditForm({
      invoice_title: '',
      supervisor_name: '',
      customer_name: '',
      payment_method: 'نقدي',
      discount_type: 'amount',
      discount_value: 0,
      items: [],
      notes: ''
    });
  };

  const saveInvoiceEdit = async () => {
    if (!editForm.customer_name.trim()) {
      alert('الرجاء إدخال اسم العميل');
      return;
    }

    try {
      console.log('Saving invoice edit for ID:', editingInvoice);
      console.log('Edit form data:', editForm);
      
      // Calculate totals
      const subtotal = editForm.items.reduce((sum, item) => sum + (item.total_price || 0), 0);
      let discountAmount = 0;
      
      if (editForm.discount_type === 'percentage') {
        discountAmount = (subtotal * parseFloat(editForm.discount_value || 0)) / 100;
      } else {
        discountAmount = parseFloat(editForm.discount_value || 0);
      }
      
      const totalAfterDiscount = subtotal - discountAmount;

      const updatedInvoice = {
        ...editForm,
        subtotal: subtotal,
        discount: discountAmount,
        total_after_discount: totalAfterDiscount,
        total_amount: totalAfterDiscount
      };

      console.log('Sending update to backend:', updatedInvoice);
      
      const response = await axios.put(`${API}/invoices/${editingInvoice}`, updatedInvoice);
      console.log('Update response:', response.data);
      
      console.log('Fetching invoices after update...');
      await fetchInvoices();
      
      cancelEdit();
      alert('تم تحديث الفاتورة بنجاح');
    } catch (error) {
      console.error('Error updating invoice:', error);
      console.error('Error response:', error.response?.data);
      alert('حدث خطأ في تحديث الفاتورة: ' + (error.response?.data?.detail || error.message));
    }
  };

  const updateInvoiceStatus = async (invoiceId, newStatus) => {
    try {
      await axios.put(`${API}/invoices/${invoiceId}/status`, 
        { status: newStatus }, {
        headers: { 'Content-Type': 'application/json' }
      });
      fetchInvoices();
      alert('تم تحديث حالة الفاتورة');
    } catch (error) {
      console.error('Error updating invoice status:', error);
      alert('حدث خطأ في تحديث حالة الفاتورة');
    }
  };

  // Payment method conversion functions
  const openPaymentMethodModal = (invoice) => {
    setSelectedInvoiceForPayment(invoice);
    setNewPaymentMethod(invoice.payment_method);
    setShowPaymentMethodModal(true);
  };

  const closePaymentMethodModal = () => {
    setShowPaymentMethodModal(false);
    setSelectedInvoiceForPayment(null);
    setNewPaymentMethod('نقدي');
  };

  const changePaymentMethod = async () => {
    if (!selectedInvoiceForPayment || newPaymentMethod === selectedInvoiceForPayment.payment_method) {
      alert('لم يتم تغيير طريقة الدفع');
      return;
    }

    try {
      const response = await axios.put(
        `${API}/invoices/${selectedInvoiceForPayment.id}/change-payment-method?new_payment_method=${encodeURIComponent(newPaymentMethod)}&username=main`
      );
      
      alert(response.data.message || 'تم تحويل طريقة الدفع بنجاح');
      fetchInvoices();
      closePaymentMethodModal();
    } catch (error) {
      console.error('Error changing payment method:', error);
      alert('حدث خطأ في تحويل طريقة الدفع: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Invoice cancellation functions
  const openCancelModal = (invoice) => {
    setSelectedInvoiceForCancel(invoice);
    setShowCancelModal(true);
  };

  const closeCancelModal = () => {
    setShowCancelModal(false);
    setSelectedInvoiceForCancel(null);
  };

  const cancelInvoice = async () => {
    if (!selectedInvoiceForCancel) return;

    try {
      const response = await axios.delete(
        `${API}/invoices/${selectedInvoiceForCancel.id}/cancel?username=main`
      );
      
      alert(response.data.message || 'تم إلغاء الفاتورة بنجاح');
      fetchInvoices();
      closeCancelModal();
    } catch (error) {
      console.error('Error canceling invoice:', error);
      alert('حدث خطأ في إلغاء الفاتورة: ' + (error.response?.data?.detail || error.message));
    }
  };

  const printInvoice = (invoice) => {
    const printContent = `
      <!DOCTYPE html>
      <html dir="rtl">
      <head>
        <meta charset="UTF-8">
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            direction: rtl;
            font-size: 15px;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
            margin-bottom: 20px;
          }
          .company-info {
            text-align: right;
          }
          .company-name {
            font-size: 32px;
            font-weight: bold;
            color: #000;
            margin: 0;
          }
          .company-subtitle {
            font-size: 20px;
            margin: 5px 0;
            color: #666;
          }
          .company-details {
            font-size: 16px;
            margin: 2px 0;
            color: #333;
          }
          .logo-section {
            text-align: center;
            flex: 1;
          }
          .invoice-title {
            font-size: 22px;
            font-weight: bold;
            background-color: #ff4444;
            color: white;
            padding: 8px 20px;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 10px;
          }
          .invoice-number {
            font-size: 20px;
            font-weight: bold;
            color: #ff4444;
          }
          .customer-info {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
          }
          .customer-details {
            text-align: right;
          }
          .date-info {
            text-align: left;
          }
          .products-table {
            width: 100%;
            border-collapse: collapse;
            border: 2px solid #000;
            margin: 20px 0;
          }
          .products-table th,
          .products-table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: center;
          }
          .products-table th {
            background-color: #f0f0f0;
            font-weight: bold;
          }
          .footer {
            margin-top: 30px;
            border-top: 1px solid #ccc;
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: #666;
          }
          .total-section {
            text-align: left;
            margin-top: 10px;
          }
          .total-amount {
            font-size: 20px;
            font-weight: bold;
            border: 2px solid #000;
            padding: 10px;
            display: inline-block;
            background-color: #f9f9f9;
          }
          @media print {
            body { margin: 0; padding: 10px; }
          }
        </style>
      </head>
      <body>
        <!-- Header Section -->
        <div class="header">
          <div class="company-info">
            <h1 class="company-name">شركة ماستر سيل</h1>
            <p class="company-subtitle">تصنيع جميع أنواع الأويل سيل</p>
            <p class="company-details">جميع الأقطار حتى ٥٠٠مل</p>
            <p class="company-details">هيدروليك - نيوماتيك</p>
          </div>
          
          <div class="logo-section">
            <img src="https://customer-assets.emergentagent.com/job_oilseal-mgmt/artifacts/42i3e7yn_WhatsApp%20Image%202025-07-31%20at%2015.14.10_e8c55120.jpg" 
                 alt="Master Seal Logo" 
                 style="max-width: 120px; max-height: 80px; margin-bottom: 10px;">
            <div class="invoice-title">${invoice.invoice_title || 'عرض سعر'}</div>
            <div class="invoice-number">${invoice.invoice_number}</div>
          </div>
        </div>

        <!-- Customer and Date Info -->
        <div class="customer-info">
          <div class="customer-details">
            <p><strong>السادة:</strong> ${invoice.customer_name}</p>
            <p><strong>العنوان:</strong> ${invoice.customer_address || '........................'}</p>
          </div>
          <div class="date-info">
            <p><strong>تحرير في:</strong> ${new Date(invoice.date).toLocaleDateString('ar-EG')}</p>
            <p><strong>Date:</strong> ${new Date(invoice.date).toLocaleDateString('en-GB')}</p>
          </div>
        </div>

        <!-- Products Table -->
        <table class="products-table">
          <thead>
            <tr>
              <th style="width: 60px;">المسلسل<br>Item</th>
              <th style="width: 80px;">الكمية<br>QTY</th>
              <th style="width: 200px;">Description<br>المواصفات</th>
              <th style="width: 100px;">سعر الوحدة<br>Unit Price</th>
              <th style="width: 100px;">إجمالي<br>Total</th>
            </tr>
          </thead>
          <tbody>
            ${invoice.items.map((item, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>${item.quantity}</td>
                <td style="text-align: right;">
                  ${item.local_product_details ? 
                    `${item.local_product_details.product_size} - ${item.local_product_details.product_type}` : 
                    `${item.seal_type} - ${item.material_type}<br>
                    <small>${item.inner_diameter} × ${item.outer_diameter} × ${item.height} مم${item.wall_height ? ` (ارتفاع الحيطة: ${item.wall_height} مم)` : ""}</small>`
                  }
                </td>
                <td>ج.م ${item.unit_price.toFixed(2)}</td>
                <td>ج.م ${item.total_price.toFixed(2)}</td>
              </tr>
            `).join('')}
            <!-- Empty rows for additional items -->
            ${Array.from({length: Math.max(0, 8 - invoice.items.length)}, (_, i) => `
              <tr style="height: 40px;">
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <!-- Total Section -->
        <div class="total-section">
          <div style="text-align: left; margin-bottom: 10px;">
            ${invoice.subtotal ? `
              <div style="margin-bottom: 5px;">
                <span>المجموع الفرعي: ج.م ${invoice.subtotal.toFixed(2)}</span>
              </div>
            ` : ''}
            ${invoice.discount && invoice.discount > 0 ? `
              <div style="margin-bottom: 5px; color: #d32f2f;">
                <span>الخصم: - ج.م ${invoice.discount.toFixed(2)}</span>
                ${invoice.discount_type === 'percentage' && invoice.discount_value ? 
                  ` <small>(${invoice.discount_value}%)</small>` : ''}
              </div>
              <hr style="margin: 5px 0; border: 1px solid #000;">
            ` : ''}
          </div>
          <div class="total-amount">
            الإجمالي النهائي: ج.م ${(invoice.total_after_discount || invoice.total_amount).toFixed(2)}
          </div>
        </div>

        <!-- Additional Info -->
        <div style="margin-top: 20px; text-align: center; font-size: 13px;">
          <p><strong>ملحوظة:</strong> فقط وقدره</p>
          <div style="height: 30px; border-bottom: 1px solid #000; margin: 10px 40px;"></div>
        </div>

        <!-- Footer -->
        <div class="footer">
          <div>
            <p><strong>التوقيع:</strong></p>
            <p>موبايل: ٠١٠٢٠٦٣٠٦٧٧ - ٠١٠٦٢٣٩٠٨٧٠</p>
            <p>تليفون: ٠١٠٢٠٦٣٠٦٧٧</p>
          </div>
          <div style="text-align: left;">
            <p><strong>المستلم:</strong></p>
            <p>الحرفيين - السلام - أمام السوبر جيت</p>
            <p>موبايل: ٠١٠٢٠٦٣٠٦٧٧ - ٠١٠٦٢٣٩٠٨٧٠</p>
          </div>
        </div>

        <!-- Note -->
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
          <p>يقر المشتري بأنه قام بمعاينة البضاعة وقبولها</p>
        </div>
      </body>
      </html>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  const clearAllInvoices = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع الفواتير؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    try {
      await axios.delete(`${API}/invoices/clear-all`);
      fetchInvoices();
      alert('تم حذف جميع الفواتير');
    } catch (error) {
      console.error('Error clearing invoices:', error);
      alert('حدث خطأ في حذف البيانات');
    }
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
          <button 
            onClick={clearAllInvoices}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
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
                <th className="border border-gray-300 p-2">المجموع الفرعي</th>
                <th className="border border-gray-300 p-2">الخصم</th>  
                <th className="border border-gray-300 p-2">الإجمالي النهائي</th>
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
                    ج.م {invoice.subtotal?.toFixed(2) || (invoice.total_amount?.toFixed(2)) || '0.00'}
                  </td>
                  <td className="border border-gray-300 p-2 text-red-600">
                    {invoice.discount && invoice.discount > 0 ? (
                      <div>
                        <span>ج.م {invoice.discount.toFixed(2)}</span>
                        {invoice.discount_type === 'percentage' && invoice.discount_value && (
                          <small className="block text-xs">(%{invoice.discount_value})</small>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400">لا يوجد</span>
                    )}
                  </td>
                  <td className="border border-gray-300 p-2 font-semibold text-green-600">
                    ج.م {(invoice.total_after_discount || invoice.total_amount)?.toFixed(2) || '0.00'}
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
                    <div className="flex flex-wrap gap-1">
                      <button
                        onClick={() => printInvoice(invoice)}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                        title="طباعة الفاتورة"
                      >
                        طباعة
                      </button>
                      <button
                        onClick={() => startEditInvoice(invoice)}
                        className="bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                        title="تعديل الفاتورة"
                      >
                        تعديل
                      </button>
                      <button
                        onClick={() => openPaymentMethodModal(invoice)}
                        className="bg-orange-500 text-white px-2 py-1 rounded text-xs hover:bg-orange-600"
                        title="تحويل طريقة الدفع"
                      >
                        تحويل دفع
                      </button>
                      <button
                        onClick={() => openCancelModal(invoice)}
                        className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                        title="إلغاء الفاتورة واسترداد المواد"
                      >
                        إلغاء فاتورة
                      </button>
                      <button
                        onClick={() => deleteInvoice(invoice.id)}
                        className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                        title="حذف الفاتورة"
                      >
                        حذف
                      </button>
                      {invoice.status === 'انتظار' && (
                        <button
                          onClick={() => updateInvoiceStatus(invoice.id, 'تم التنفيذ')}
                          className="bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                          title="تم التنفيذ"
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

      {/* Edit Invoice Modal */}
      {editingInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-4xl max-h-screen overflow-y-auto" dir="rtl">
            <h3 className="text-xl font-semibold mb-4">تعديل الفاتورة</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1">عنوان الفاتورة</label>
                <input
                  type="text"
                  value={editForm.invoice_title}
                  onChange={(e) => setEditForm({...editForm, invoice_title: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="عنوان الفاتورة (اختياري)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">اسم المشرف</label>
                <input
                  type="text"
                  value={editForm.supervisor_name}
                  onChange={(e) => setEditForm({...editForm, supervisor_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="اسم المشرف (اختياري)"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">اسم العميل</label>
                <input
                  type="text"
                  value={editForm.customer_name}
                  onChange={(e) => setEditForm({...editForm, customer_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="اسم العميل"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">طريقة الدفع</label>
                <select
                  value={editForm.payment_method}
                  onChange={(e) => setEditForm({...editForm, payment_method: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="نقدي">نقدي</option>
                  <option value="فودافون كاش الصاوي">فودافون كاش الصاوي</option>
                  <option value="فودافون كاش وائل">فودافون كاش وائل</option>
                  <option value="آجل">آجل</option>
                  <option value="انستا باي">انستا باي</option>
                  <option value="Yad_Elsawy">Yad Elsawy</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">نوع الخصم</label>
                <select
                  value={editForm.discount_type}
                  onChange={(e) => setEditForm({...editForm, discount_type: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="amount">مبلغ ثابت</option>
                  <option value="percentage">نسبة مئوية</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">قيمة الخصم</label>
                <input
                  type="number"
                  step="0.01"
                  value={editForm.discount_value}
                  onChange={(e) => setEditForm({...editForm, discount_value: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder={editForm.discount_type === 'percentage' ? '0-100' : '0.00'}
                />
              </div>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">ملاحظات</label>
              <textarea
                value={editForm.notes}
                onChange={(e) => setEditForm({...editForm, notes: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded"
                rows="3"
                placeholder="ملاحظات إضافية (اختياري)"
              />
            </div>
            
            {/* Items Display with Edit capability */}
            <div className="mb-4">
              <h4 className="text-lg font-medium mb-2">عناصر الفاتورة</h4>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border border-gray-300 p-2">المنتج</th>
                      <th className="border border-gray-300 p-2">الكمية</th>
                      <th className="border border-gray-300 p-2">سعر الوحدة</th>
                      <th className="border border-gray-300 p-2">الإجمالي</th>
                      <th className="border border-gray-300 p-2">إجراءات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {editForm.items.map((item, index) => (
                      <tr key={index}>
                        <td className="border border-gray-300 p-2">
                          {item.product_type === 'local' || item.local_product_details ? (
                            <input
                              type="text"
                              value={item.product_name || `${item.local_product_details?.product_size || ''} - ${item.local_product_details?.product_type || ''}`}
                              onChange={(e) => {
                                const newItems = [...editForm.items];
                                newItems[index].product_name = e.target.value;
                                setEditForm({...editForm, items: newItems});
                              }}
                              className="w-full p-1 border border-gray-300 rounded"
                              placeholder="مقاس المنتج - نوع المنتج"
                            />
                          ) : (
                            <div className="space-y-1">
                              {/* Seal Type */}
                              <div className="flex items-center space-x-2 space-x-reverse">
                                <label className="text-xs font-medium w-16">نوع السيل:</label>
                                <select
                                  value={item.seal_type || ''}
                                  onChange={(e) => {
                                    const newItems = [...editForm.items];
                                    newItems[index].seal_type = e.target.value;
                                    setEditForm({...editForm, items: newItems});
                                  }}
                                  className="flex-1 p-1 text-xs border border-gray-300 rounded"
                                >
                                  <option value="">اختر النوع</option>
                                  <option value="RSL">RSL</option>
                                  <option value="RS">RS</option>
                                  <option value="RSS">RSS</option>
                                  <option value="RSE">RSE</option>
                                  <option value="B17">B17</option>
                                  <option value="B3">B3</option>
                                  <option value="B14">B14</option>
                                  <option value="B1">B1</option>
                                  <option value="R15">R15</option>
                                  <option value="R17">R17</option>
                                  <option value="W1">W1</option>
                                  <option value="W4">W4</option>
                                  <option value="W5">W5</option>
                                  <option value="W11">W11</option>
                                  <option value="WBT">WBT</option>
                                  <option value="XR">XR</option>
                                  <option value="CH">CH</option>
                                  <option value="VR">VR</option>
                                </select>
                              </div>
                              
                              {/* Material Type */}
                              <div className="flex items-center space-x-2 space-x-reverse">
                                <label className="text-xs font-medium w-16">نوع الخامة:</label>
                                <select
                                  value={item.material_type || ''}
                                  onChange={(e) => {
                                    const newItems = [...editForm.items];
                                    newItems[index].material_type = e.target.value;
                                    setEditForm({...editForm, items: newItems});
                                  }}
                                  className="flex-1 p-1 text-xs border border-gray-300 rounded"
                                >
                                  <option value="">اختر الخامة</option>
                                  <option value="NBR">NBR</option>
                                  <option value="BUR">BUR</option>
                                  <option value="BT">BT</option>
                                  <option value="VT">VT</option>
                                  <option value="BOOM">BOOM</option>
                                </select>
                              </div>
                              
                              {/* Dimensions */}
                              <div className="flex items-center space-x-1 space-x-reverse">
                                <input
                                  type="number"
                                  step="0.1"
                                  value={item.inner_diameter || ''}
                                  onChange={(e) => {
                                    const newItems = [...editForm.items];
                                    newItems[index].inner_diameter = parseFloat(e.target.value) || 0;
                                    setEditForm({...editForm, items: newItems});
                                  }}
                                  placeholder="داخلي"
                                  className="w-12 p-1 text-xs border border-gray-300 rounded"
                                />
                                <span className="text-xs">×</span>
                                <input
                                  type="number"
                                  step="0.1"
                                  value={item.outer_diameter || ''}
                                  onChange={(e) => {
                                    const newItems = [...editForm.items];
                                    newItems[index].outer_diameter = parseFloat(e.target.value) || 0;
                                    setEditForm({...editForm, items: newItems});
                                  }}
                                  placeholder="خارجي"
                                  className="w-12 p-1 text-xs border border-gray-300 rounded"
                                />
                                <span className="text-xs">×</span>
                                <input
                                  type="number"
                                  step="0.1"
                                  value={item.height || ''}
                                  onChange={(e) => {
                                    const newItems = [...editForm.items];
                                    newItems[index].height = parseFloat(e.target.value) || 0;
                                    setEditForm({...editForm, items: newItems});
                                  }}
                                  placeholder="ارتفاع"
                                  className="w-12 p-1 text-xs border border-gray-300 rounded"
                                />
                              </div>
                            </div>
                          )}
                        </td>
                        <td className="border border-gray-300 p-2">
                          <input
                            type="number"
                            value={item.quantity}
                            onChange={(e) => {
                              const newItems = [...editForm.items];
                              newItems[index].quantity = parseInt(e.target.value) || 0;
                              newItems[index].total_price = newItems[index].unit_price * newItems[index].quantity;
                              setEditForm({...editForm, items: newItems});
                            }}
                            className="w-full p-1 border border-gray-300 rounded"
                          />
                        </td>
                        <td className="border border-gray-300 p-2">
                          <input
                            type="number"
                            step="0.01"
                            value={item.unit_price}
                            onChange={(e) => {
                              const newItems = [...editForm.items];
                              newItems[index].unit_price = parseFloat(e.target.value) || 0;
                              newItems[index].total_price = newItems[index].unit_price * newItems[index].quantity;
                              setEditForm({...editForm, items: newItems});
                            }}
                            className="w-full p-1 border border-gray-300 rounded"
                          />
                        </td>
                        <td className="border border-gray-300 p-2 font-semibold">
                          ج.م {(item.total_price || 0).toFixed(2)}
                        </td>
                        <td className="border border-gray-300 p-2">
                          <button
                            onClick={() => {
                              const newItems = editForm.items.filter((_, i) => i !== index);
                              setEditForm({...editForm, items: newItems});
                            }}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            حذف
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Add Product Button */}
              <button
                onClick={() => {
                  // Add a new empty item for editing
                  const newItem = {
                    seal_type: '',
                    material_type: '',
                    inner_diameter: '',
                    outer_diameter: '',
                    height: '',
                    quantity: 1,
                    unit_price: 0,
                    total_price: 0
                  };
                  setEditForm({
                    ...editForm,
                    items: [...editForm.items, newItem]
                  });
                }}
                className="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                إضافة منتج جديد
              </button>
            </div>
            
            {/* Action Buttons */}
            <div className="flex justify-end space-x-4 space-x-reverse">
              <button
                onClick={cancelEdit}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
              <button
                onClick={saveInvoiceEdit}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                حفظ التعديلات
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Payment Method Conversion Modal */}
      {showPaymentMethodModal && selectedInvoiceForPayment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md" dir="rtl">
            <h3 className="text-xl font-semibold mb-4 text-orange-600">تحويل طريقة الدفع</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>رقم الفاتورة:</strong> {selectedInvoiceForPayment.invoice_number}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>العميل:</strong> {selectedInvoiceForPayment.customer_name}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                <strong>المبلغ:</strong> ج.م {(selectedInvoiceForPayment.total_amount || 0).toFixed(2)}
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">الطريقة الحالية:</label>
              <div className="p-2 bg-gray-100 rounded text-sm">
                {selectedInvoiceForPayment.payment_method}
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">الطريقة الجديدة:</label>
              <select
                value={newPaymentMethod}
                onChange={(e) => setNewPaymentMethod(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="نقدي">نقدي</option>
                <option value="آجل">آجل</option>
                <option value="فودافون كاش محمد الصاوي">فودافون كاش محمد الصاوي</option>
                <option value="فودافون كاش وائل محمد">فودافون كاش وائل محمد</option>
                <option value="انستاباي">انستاباي</option>
                <option value="يد الصاوي">يد الصاوي</option>
              </select>
            </div>

            <div className="flex justify-end space-x-4 space-x-reverse">
              <button
                onClick={closePaymentMethodModal}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
              <button
                onClick={changePaymentMethod}
                className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600"
                disabled={newPaymentMethod === selectedInvoiceForPayment.payment_method}
              >
                تحويل طريقة الدفع
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invoice Cancellation Modal */}
      {showCancelModal && selectedInvoiceForCancel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md" dir="rtl">
            <h3 className="text-xl font-semibold mb-4 text-red-600">إلغاء الفاتورة</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>رقم الفاتورة:</strong> {selectedInvoiceForCancel.invoice_number}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>العميل:</strong> {selectedInvoiceForCancel.customer_name}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <strong>المبلغ:</strong> ج.م {(selectedInvoiceForCancel.total_amount || 0).toFixed(2)}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                <strong>طريقة الدفع:</strong> {selectedInvoiceForCancel.payment_method}
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-6">
              <h4 className="font-medium text-yellow-800 mb-2">⚠️ تحذير: عملية إلغاء الفاتورة</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• سيتم حذف الفاتورة نهائياً من النظام</li>
                <li>• سيتم استرداد جميع المواد المستخدمة إلى المخزون</li>
                <li>• سيتم عكس المعاملات المالية من الخزينة</li>
                <li>• هذا الإجراء لا يمكن التراجع عنه</li>
              </ul>
            </div>

            <div className="flex justify-end space-x-4 space-x-reverse">
              <button
                onClick={closeCancelModal}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
              <button
                onClick={cancelInvoice}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                تأكيد إلغاء الفاتورة
              </button>
            </div>
          </div>
        </div>
      )}
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
  const [showAddToExisting, setShowAddToExisting] = useState(false);
  const [selectedWorkOrderId, setSelectedWorkOrderId] = useState('');
  const [selectedInvoiceForAdd, setSelectedInvoiceForAdd] = useState('');

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
      setWorkOrders([]); // Set empty array on error
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
      
      // Clean invoices data (remove MongoDB ObjectIds)
      const cleanInvoices = selectedInvoicesData.map(inv => {
        const cleanInv = { ...inv };
        if (cleanInv._id) delete cleanInv._id;
        return cleanInv;
      });
      
      // Create work order with multiple invoices
      const workOrderData = {
        title: newWorkOrder.title,
        description: newWorkOrder.description,
        priority: newWorkOrder.priority,
        invoices: cleanInvoices,
        total_amount: cleanInvoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0),
        total_items: cleanInvoices.reduce((sum, inv) => sum + (inv.items?.length || 0), 0)
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
        
        // Refresh work orders list
        await fetchWorkOrders();
      }
    } catch (error) {
      console.error('Error creating work order:', error);
      alert('حدث خطأ في إنشاء أمر الشغل: ' + (error.response?.data?.detail || error.message));
    }
  };

  const addInvoiceToExistingWorkOrder = async () => {
    if (!selectedWorkOrderId || !selectedInvoiceForAdd) {
      alert('الرجاء اختيار أمر الشغل والفاتورة');
      return;
    }

    try {
      const response = await axios.put(`${API}/work-orders/${selectedWorkOrderId}/add-invoice`, null, {
        params: { invoice_id: selectedInvoiceForAdd }
      });
      
      if (response.data) {
        alert('تم إضافة الفاتورة إلى أمر الشغل بنجاح');
        
        // Reset form
        setSelectedWorkOrderId('');
        setSelectedInvoiceForAdd('');
        setShowAddToExisting(false);
        
        // Refresh work orders list
        await fetchWorkOrders();
      }
    } catch (error) {
      console.error('Error adding invoice to work order:', error);
      alert('حدث خطأ في إضافة الفاتورة: ' + (error.response?.data?.detail || error.message));
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

  const getAvailableInvoicesForAdd = () => {
    // Get invoices not already in the selected work order
    if (!selectedWorkOrderId) return getAvailableInvoices();
    
    const selectedWorkOrder = workOrders.find(wo => wo.id === selectedWorkOrderId);
    if (!selectedWorkOrder) return getAvailableInvoices();
    
    const usedInvoiceIds = selectedWorkOrder.invoices?.map(inv => inv.id) || [];
    
    return getAvailableInvoices().filter(invoice => 
      !usedInvoiceIds.includes(invoice.id)
    );
  };

  const printWorkOrder = (workOrder) => {
    const workOrderInvoices = workOrder.invoices?.map(invoiceData => 
      invoices.find(inv => inv.id === invoiceData.id) || invoiceData
    ).filter(inv => inv) || [];
    
    const totalAmount = workOrderInvoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0);
    const totalItems = workOrderInvoices.reduce((sum, inv) => sum + (inv.items?.length || 0), 0);
    
    const printContent = `
      <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h1>ماستر سيل</h1>
          <p>الحرفيين شارع السوبر جيت - 01020630677</p>
          <h2 style="color: #333; margin-top: 20px;">أمر شغل</h2>
        </div>
        
        <div style="margin-bottom: 20px;">
          <strong>رقم أمر الشغل:</strong> ${workOrder.id}<br>
          <strong>العنوان:</strong> ${workOrder.title || `أمر شغل #${workOrder.id.slice(-8)}`}<br>
          <strong>التاريخ:</strong> ${new Date(workOrder.created_at).toLocaleDateString('ar-EG')}<br>
          <strong>الحالة:</strong> ${workOrder.status || 'جديد'}<br>
          <strong>عدد الفواتير:</strong> ${workOrderInvoices.length}<br>
          <strong>إجمالي المبلغ:</strong> ج.م ${totalAmount.toFixed(2)}
          ${workOrder.description ? `<br><strong>الوصف:</strong> ${workOrder.description}` : ''}
          ${workOrder.supervisor_name ? `<br><strong>المشرف على التصنيع:</strong> ${workOrder.supervisor_name}` : ''}
          ${workOrder.is_daily ? `<br><strong>نوع الأمر:</strong> أمر شغل يومي تلقائي` : ''}
        </div>

        <h3 style="color: #333; margin-bottom: 10px;">الفواتير المدرجة:</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #f0f0f0;">
              <th style="border: 1px solid #ddd; padding: 8px;">رقم الفاتورة</th>
              <th style="border: 1px solid #ddd; padding: 8px;">العميل</th>
              <th style="border: 1px solid #ddd; padding: 8px;">التاريخ</th>
              <th style="border: 1px solid #ddd; padding: 8px;">المبلغ</th>
              <th style="border: 1px solid #ddd; padding: 8px;">عدد المنتجات</th>
            </tr>
          </thead>
          <tbody>
            ${workOrderInvoices.map(invoice => `
              <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">${invoice.invoice_number}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${invoice.customer_name}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${new Date(invoice.date).toLocaleDateString('ar-EG')}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">ج.م ${invoice.total_amount?.toFixed(2) || '0.00'}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">${invoice.items?.length || 0}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h3 style="color: #333; margin-bottom: 10px;">تفاصيل المنتجات:</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <thead>
            <tr style="background-color: #f0f0f0;">
              <th style="border: 1px solid #ddd; padding: 8px;">رقم الفاتورة</th>
              <th style="border: 1px solid #ddd; padding: 8px;">نوع السيل</th>
              <th style="border: 1px solid #ddd; padding: 8px;">نوع الخامة</th>
              <th style="border: 1px solid #ddd; padding: 8px;">المقاس</th>
              <th style="border: 1px solid #ddd; padding: 8px;">الكمية</th>
              <th style="border: 1px solid #ddd; padding: 8px;">الخامة المستخدمة</th>
              <th style="border: 1px solid #ddd; padding: 8px;">كود الوحدة</th>
            </tr>
          </thead>
          <tbody>
            ${workOrderInvoices.map(invoice => 
              invoice.items?.map(item => `
                <tr>
                  <td style="border: 1px solid #ddd; padding: 8px;">${invoice.invoice_number}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">${item.local_product_details ? item.local_product_details.product_type : (item.seal_type || 'غير محدد')}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">${item.local_product_details ? 'محلي' : (item.material_type || 'غير محدد')}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">${item.local_product_details ? `${item.local_product_details.product_size} - ${item.local_product_details.product_type}` : (item.inner_diameter && item.outer_diameter && item.height ? `${item.inner_diameter} × ${item.outer_diameter} × ${item.height}${item.wall_height ? ` (ارتفاع الحيطة: ${item.wall_height})` : ''}` : 'غير محدد')}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">${item.quantity}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">${item.local_product_details ? 'محلي' : (item.material_used || 'غير محدد')}</td>
                  <td style="border: 1px solid #ddd; padding: 8px;">
                    ${item.local_product_details ? 
                      'محلي' :
                      item.material_details ? 
                        (item.material_details.is_finished_product ? 
                          'مخزن انتاج تام' : 
                          `${item.material_details.unit_code} / ${item.material_details.inner_diameter}-${item.material_details.outer_diameter}`
                        ) : 
                        `${item.material_used || 'غير محدد'} / معلومات غير متوفرة`
                    }
                  </td>
                </tr>
              `).join('') || ''
            ).join('')}
          </tbody>
        </table>
        
        <div style="margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px;">
          <div style="float: left;">
            <strong>ملاحظات التصنيع:</strong><br>
            <div style="margin-top: 10px; height: 50px; border: 1px solid #ddd;"></div>
          </div>
          <div style="float: right;">
            <strong>توقيع المسؤول:</strong><br>
            <div style="margin-top: 10px; height: 50px; border: 1px solid #ddd; width: 150px;"></div>
          </div>
          <div style="clear: both;"></div>
        </div>
      </div>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.print();
  };

  const clearAllWorkOrders = async () => {
    if (!confirm('هل أنت متأكد من حذف جميع أوامر الشغل؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    try {
      await axios.delete(`${API}/work-orders/clear-all`);
      fetchWorkOrders();
      alert('تم حذف جميع أوامر الشغل');
    } catch (error) {
      console.error('Error clearing work orders:', error);
      alert('حدث خطأ في حذف البيانات');
    }
  };

  const deleteWorkOrder = async (workOrderId) => {
    if (!confirm('هل أنت متأكد من حذف أمر الشغل هذا؟')) return;
    
    try {
      await axios.delete(`${API}/work-orders/${workOrderId}`);
      fetchWorkOrders();
      alert('تم حذف أمر الشغل بنجاح');
    } catch (error) {
      console.error('Error deleting work order:', error);
      alert('حدث خطأ في حذف أمر الشغل');
    }
  };

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">أمر شغل</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button 
            onClick={clearAllWorkOrders}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
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
          <button 
            onClick={() => setShowAddToExisting(!showAddToExisting)}
            className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
            {showAddToExisting ? 'إخفاء' : 'إضافة فاتورة لأمر موجود'}
          </button>
          <select className="border border-gray-300 rounded px-3 py-2">
            <option>يومي</option>
            <option>أسبوعي</option>
            <option>شهري</option>
            <option>سنوي</option>
          </select>
        </div>
      </div>

      {/* Add Invoice to Existing Work Order */}
      {showAddToExisting && (
        <div className="bg-yellow-50 p-6 rounded-lg shadow-md mb-6 border border-yellow-200">
          <h3 className="text-lg font-semibold mb-4 text-yellow-800">إضافة فاتورة إلى أمر شغل موجود</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">اختيار أمر الشغل</label>
              <select
                value={selectedWorkOrderId}
                onChange={(e) => setSelectedWorkOrderId(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
              >
                <option value="">اختر أمر الشغل</option>
                {workOrders.map(workOrder => (
                  <option key={workOrder.id} value={workOrder.id}>
                    {workOrder.title || `أمر شغل #${workOrder.id.slice(-8)}`} 
                    ({workOrder.invoices?.length || 0} فاتورة)
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">اختيار الفاتورة</label>
              <select
                value={selectedInvoiceForAdd}
                onChange={(e) => setSelectedInvoiceForAdd(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
                disabled={!selectedWorkOrderId}
              >
                <option value="">اختر الفاتورة</option>
                {getAvailableInvoicesForAdd().map(invoice => (
                  <option key={invoice.id} value={invoice.id}>
                    {invoice.invoice_number} - {invoice.customer_name} 
                    (ج.م {invoice.total_amount?.toFixed(2) || '0.00'})
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex space-x-4 space-x-reverse">
            <button
              onClick={addInvoiceToExistingWorkOrder}
              className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
              disabled={!selectedWorkOrderId || !selectedInvoiceForAdd}
            >
              إضافة الفاتورة
            </button>
            <button
              onClick={() => {
                setShowAddToExisting(false);
                setSelectedWorkOrderId('');
                setSelectedInvoiceForAdd('');
              }}
              className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
            >
              إلغاء
            </button>
          </div>
        </div>
      )}

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
        <h3 className="text-lg font-semibold mb-4">أوامر الشغل ({workOrders.length})</h3>
        
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
                  {workOrder.supervisor_name && (
                    <p><strong>المشرف على التصنيع:</strong> {workOrder.supervisor_name}</p>
                  )}
                  {workOrder.is_daily && (
                    <p><strong>نوع الأمر:</strong> <span className="text-green-600">أمر شغل يومي تلقائي</span></p>
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
                            {item.material_details ? (
                              item.material_details.is_finished_product ? (
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                                  منتج جاهز
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                                  {item.material_details.material_type}
                                </span>
                              )
                            ) : (
                              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                                {item.material_used || 'غير محدد'}
                              </span>
                            )}
                          </td>
                          <td className="border border-gray-300 p-2">
                            <div className="font-mono text-sm">
                              {item.material_details ? (
                                item.material_details.is_finished_product ? (
                                  <div className="text-center font-semibold text-blue-600">
                                    مخزن انتاج تام
                                  </div>
                                ) : (
                                  <div>
                                    <div className="font-semibold">
                                      {item.unit_code_display || item.material_details.unit_code}
                                    </div>
                                    <div className="text-xs text-gray-600">
                                      {item.material_details.inner_diameter} - {item.material_details.outer_diameter}
                                    </div>
                                  </div>
                                )
                              ) : (
                                // للبيانات القديمة أو عندما لا توجد material_details
                                <div>
                                  <div className="font-semibold">{item.material_used || 'غير محدد'}</div>
                                  <div className="text-xs text-gray-600">
                                    معلومات الخامة غير متوفرة
                                  </div>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )) || []
                    )}
                  </tbody>
                </table>
              </div>
              
              {/* Work Order Actions */}
              <div className="flex space-x-4 space-x-reverse">
                <button 
                  onClick={() => printWorkOrder(workOrder)}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                  طباعة أمر الشغل
                </button>
                <button className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">
                  تعديل الحالة
                </button>
                <button 
                  onClick={() => {
                    setSelectedWorkOrderId(workOrder.id);
                    setShowAddToExisting(true);
                  }}
                  className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                  إضافة فاتورة
                </button>
                <button 
                  onClick={() => deleteWorkOrder(workOrder.id)}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
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

// Treasury Management Component
const Treasury = () => {
  const { user } = useAuth(); // للحصول على معلومات المستخدم الحالي
  const [accounts, setAccounts] = useState([
    { id: 'cash', name: 'نقدي', balance: 0, transactions: [] },
    { id: 'vodafone_elsawy', name: 'فودافون كاش محمد الصاوي', balance: 0, transactions: [] },
    { id: 'vodafone_wael', name: 'فودافون كاش وائل محمد', balance: 0, transactions: [] },
    { id: 'deferred', name: 'آجل', balance: 0, transactions: [] },
    { id: 'instapay', name: 'انستاباي', balance: 0, transactions: [] },
    { id: 'yad_elsawy', name: 'يد الصاوي', balance: 0, transactions: [] }
  ]);
  
  const [selectedAccount, setSelectedAccount] = useState('cash');
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({
    from: 'cash',
    to: 'vodafone_elsawy',
    amount: '',
    notes: ''
  });
  
  const [manualTransaction, setManualTransaction] = useState({
    account: 'cash',
    type: 'income', // income or expense
    amount: '',
    description: '',
    notes: ''
  });
  
  const [showManualForm, setShowManualForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState(''); // إضافة البحث

  useEffect(() => {
    fetchTreasuryData();
  }, []);

  const fetchTreasuryData = async () => {
    try {
      // Fetch balances and transactions from backend
      const balancesResponse = await axios.get(`${API}/treasury/balances`);
      const transactionsResponse = await axios.get(`${API}/treasury/transactions`);
      const invoicesResponse = await axios.get(`${API}/invoices`);
      const expensesResponse = await axios.get(`${API}/expenses`);
      
      const balances = balancesResponse.data;
      const manualTransactions = transactionsResponse.data;
      const invoices = invoicesResponse.data;
      const expenses = expensesResponse.data;
      
      // Update accounts with balances and transactions
      const updatedAccounts = accounts.map(account => {
        let transactions = [];
        
        // Add invoice transactions
        invoices.forEach(invoice => {
          const paymentMethodMap = {
            'نقدي': 'cash',
            'فودافون كاش محمد الصاوي': 'vodafone_elsawy', 
            'فودافون كاش وائل محمد': 'vodafone_wael',
            'آجل': 'deferred',
            'انستاباي': 'instapay',
            'يد الصاوي': 'yad_elsawy'
          };
          
          if (paymentMethodMap[invoice.payment_method] === account.id) {
            transactions.push({
              id: `inv-${invoice.id}`,
              type: 'income',
              amount: invoice.total_amount || 0,
              description: `فاتورة رقم ${invoice.invoice_number}`,
              date: invoice.date,
              reference: `العميل: ${invoice.customer_name}`
            });
          }
        });
        
        // Add expense transactions (only from cash account)
        if (account.id === 'cash') {
          expenses.forEach(expense => {
            transactions.push({
              id: `exp-${expense.id}`,
              type: 'expense',
              amount: expense.amount || 0,
              description: expense.description || 'مصروف',
              date: expense.date,
              category: expense.category
            });
          });
        }
        
        // Add manual transactions
        manualTransactions
          .filter(transaction => transaction.account_id === account.id)
          .forEach(transaction => {
            transactions.push({
              id: transaction.id,
              type: transaction.transaction_type,
              amount: transaction.amount,
              description: transaction.description,
              date: transaction.date,
              reference: transaction.reference
            });
          });
        
        return {
          ...account,
          balance: balances[account.id] || 0,
          transactions: transactions.sort((a, b) => new Date(b.date) - new Date(a.date))
        };
      });
      
      setAccounts(updatedAccounts);
    } catch (error) {
      console.error('Error fetching treasury data:', error);
    }
  };

  const handleTransfer = async () => {
    if (!transferData.amount || parseFloat(transferData.amount) <= 0) {
      alert('الرجاء إدخال مبلغ صحيح');
      return;
    }
    
    const amount = parseFloat(transferData.amount);
    const fromAccount = accounts.find(acc => acc.id === transferData.from);
    
    if (fromAccount.balance < amount) {
      alert('الرصيد غير كافي');
      return;
    }
    
    try {
      await axios.post(`${API}/treasury/transfer`, {
        from_account: transferData.from,
        to_account: transferData.to,
        amount: amount,
        notes: transferData.notes
      });
      
      // Refresh data
      fetchTreasuryData();
      
      setShowTransferModal(false);
      setTransferData({ from: 'cash', to: 'vodafone_elsawy', amount: '', notes: '' });
      alert('تم التحويل بنجاح');
    } catch (error) {
      console.error('Error processing transfer:', error);
      alert('حدث خطأ في التحويل');
    }
  };

  const handleManualTransaction = async () => {
    if (!manualTransaction.amount || parseFloat(manualTransaction.amount) <= 0) {
      alert('الرجاء إدخال مبلغ صحيح');
      return;
    }
    
    const amount = parseFloat(manualTransaction.amount);
    
    try {
      await axios.post(`${API}/treasury/transactions`, {
        account_id: manualTransaction.account,
        transaction_type: manualTransaction.type,
        amount: amount,
        description: manualTransaction.description,
        reference: manualTransaction.notes || 'إدخال يدوي'
      });
      
      // Refresh data
      fetchTreasuryData();
      
      setShowManualForm(false);
      setManualTransaction({
        account: 'cash',
        type: 'income',
        amount: '',
        description: '',
        notes: ''
      });
      alert('تم إضافة العملية بنجاح');
    } catch (error) {
      console.error('Error processing manual transaction:', error);
      alert('حدث خطأ في إضافة العملية');
    }
  };

  const clearAccount = async (accountId) => {
    if (!confirm('هل أنت متأكد من تصفير هذا الحساب؟ هذا الإجراء لا يمكن التراجع عنه.')) return;
    
    const account = accounts.find(acc => acc.id === accountId);
    if (!account || account.balance === 0) {
      alert('الحساب فارغ بالفعل أو غير موجود');
      return;
    }
    
    try {
      // Create expense transaction to zero the account
      await axios.post(`${API}/treasury/transactions`, {
        account_id: accountId,
        transaction_type: 'expense',
        amount: account.balance,
        description: `تصفير حساب ${account.name}`,
        reference: 'تصفير بواسطة المدير'
      });
      
      // Refresh data
      fetchTreasuryData();
      alert(`تم تصفير حساب ${account.name} بنجاح`);
    } catch (error) {
      console.error('Error clearing account:', error);
      alert('حدث خطأ في تصفير الحساب');
    }
  };

  // Treasury Reset Function - Only for Elsawy
  const resetTreasury = async () => {
    if (user?.username !== 'Elsawy') {
      alert('غير مصرح لك بتنفيذ هذه العملية');
      return;
    }

    // Triple confirmation for this critical operation
    const firstConfirm = confirm('⚠️ تحذير: هذا الإجراء سيحذف جميع بيانات الخزينة ولا يمكن التراجع عنه!\nهل أنت متأكد من المتابعة؟');
    if (!firstConfirm) return;

    const secondConfirm = confirm('⚠️ تأكيد ثاني: سيتم حذف جميع المعاملات والأرصدة نهائياً!\nاكتب "نعم" للتأكيد:');
    if (!secondConfirm) return;

    const finalConfirm = prompt('⚠️ للتأكيد النهائي، اكتب بالضبط: "احذف كل شيء"');
    if (finalConfirm !== 'احذف كل شيء') {
      alert('تم إلغاء العملية');
      return;
    }

    try {
      const response = await axios.post(`${API}/treasury/reset`, null, {
        params: { username: user.username }
      });

      alert(`✅ تم مسح جميع بيانات الخزينة بنجاح!\nتم حذف ${response.data.deleted_treasury_transactions} معاملة`);
      
      // Refresh data
      fetchTreasuryData();
    } catch (error) {
      console.error('Error resetting treasury:', error);
      alert('حدث خطأ في مسح الخزينة: ' + (error.response?.data?.detail || error.message));
    }
  };

  const selectedAccountData = accounts.find(acc => acc.id === selectedAccount);

  return (
    <div className="p-6" dir="rtl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-4">الخزينة - إدارة الأموال</h2>
        
        <div className="flex space-x-4 space-x-reverse mb-4">
          <button 
            onClick={() => setShowTransferModal(true)}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            تحويل أموال
          </button>
          <button 
            onClick={() => setShowManualForm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            إضافة عملية يدوية
          </button>
          <button 
            onClick={fetchTreasuryData}
            className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
            إعادة تحميل
          </button>
          <button 
            onClick={() => window.print()}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
            طباعة تقرير
          </button>
          {user?.username === 'Elsawy' && (
            <button 
              onClick={resetTreasury}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 font-bold border-2 border-red-800">
              ⚠️ مسح الخزينة بالكامل
            </button>
          )}
          {user?.username === 'Elsawy' && selectedAccount === 'yad_elsawy' && selectedAccountData?.balance > 0 && (
            <button 
              onClick={() => clearAccount(selectedAccount)}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
              تصفير حساب يد الصاوي
            </button>
          )}
        </div>
      </div>

      {/* Accounts Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {accounts.map(account => (
          <div 
            key={account.id}
            className={`p-4 rounded-lg shadow cursor-pointer transition-colors ${
              selectedAccount === account.id 
                ? 'bg-blue-100 border-2 border-blue-500' 
                : 'bg-white hover:bg-gray-50'
            }`}
            onClick={() => setSelectedAccount(account.id)}
          >
            <h3 className="font-semibold text-gray-800 mb-2">{account.name}</h3>
            <p className={`text-2xl font-bold ${
              account.balance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ج.م {account.balance.toFixed(2)}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {account.transactions.length} عملية
            </p>
          </div>
        ))}
      </div>

      {/* Account Details */}
      {selectedAccountData && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">
            تفاصيل حساب: {selectedAccountData.name}
          </h3>
          
          {/* Search Bar */}
          <div className="mb-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="البحث في المعاملات..."
              className="w-full p-3 border border-gray-300 rounded-lg"
            />
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-2">التاريخ</th>
                  <th className="border border-gray-300 p-2">النوع</th>
                  <th className="border border-gray-300 p-2">الوصف</th>
                  <th className="border border-gray-300 p-2">المبلغ</th>
                  <th className="border border-gray-300 p-2">المرجع</th>
                </tr>
              </thead>
              <tbody>
                {selectedAccountData.transactions
                  .filter(transaction => 
                    transaction.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (transaction.reference && transaction.reference.toLowerCase().includes(searchTerm.toLowerCase())) ||
                    (transaction.category && transaction.category.toLowerCase().includes(searchTerm.toLowerCase()))
                  )
                  .map((transaction, index) => (
                  <tr key={transaction.id || index}>
                    <td className="border border-gray-300 p-2">
                      {new Date(transaction.date).toLocaleDateString('ar-EG')}
                    </td>
                    <td className="border border-gray-300 p-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        transaction.type === 'income' ? 'bg-green-100 text-green-800' :
                        transaction.type === 'expense' ? 'bg-red-100 text-red-800' :
                        transaction.type === 'transfer_in' ? 'bg-blue-100 text-blue-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {transaction.type === 'income' ? 'دخل' :
                         transaction.type === 'expense' ? 'مصروف' :
                         transaction.type === 'transfer_in' ? 'تحويل وارد' : 'تحويل صادر'}
                      </span>
                    </td>
                    <td className="border border-gray-300 p-2">{transaction.description}</td>
                    <td className="border border-gray-300 p-2">
                      <span className={
                        transaction.type === 'income' || transaction.type === 'transfer_in' 
                          ? 'text-green-600 font-semibold' 
                          : 'text-red-600 font-semibold'
                      }>
                        {transaction.type === 'income' || transaction.type === 'transfer_in' ? '+' : '-'}
                        ج.م {transaction.amount.toFixed(2)}
                      </span>
                    </td>
                    <td className="border border-gray-300 p-2 text-sm text-gray-600">
                      {transaction.reference || transaction.category || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {selectedAccountData.transactions.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                لا توجد عمليات لهذا الحساب
              </div>
            )}
          </div>
        </div>
      )}

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">تحويل أموال بين الحسابات</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">من حساب</label>
                <select
                  value={transferData.from}
                  onChange={(e) => setTransferData({...transferData, from: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  {accounts.map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name} (ج.م {account.balance.toFixed(2)})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">إلى حساب</label>
                <select
                  value={transferData.to}
                  onChange={(e) => setTransferData({...transferData, to: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  {accounts.filter(acc => acc.id !== transferData.from).map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">المبلغ</label>
                <input
                  type="number"
                  value={transferData.amount}
                  onChange={(e) => setTransferData({...transferData, amount: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">ملاحظات</label>
                <input
                  type="text"
                  value={transferData.notes}
                  onChange={(e) => setTransferData({...transferData, notes: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="ملاحظات إضافية (اختياري)"
                />
              </div>
            </div>
            
            <div className="flex space-x-4 space-x-reverse mt-6">
              <button
                onClick={handleTransfer}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
              >
                تأكيد التحويل
              </button>
              <button
                onClick={() => setShowTransferModal(false)}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                إلغاء
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Transaction Modal */}
      {showManualForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">إضافة عملية يدوية</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">الحساب</label>
                <select
                  value={manualTransaction.account}
                  onChange={(e) => setManualTransaction({...manualTransaction, account: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  {accounts.map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">نوع العملية</label>
                <select
                  value={manualTransaction.type}
                  onChange={(e) => setManualTransaction({...manualTransaction, type: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="income">دخل</option>
                  <option value="expense">مصروف</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">المبلغ</label>
                <input
                  type="number"
                  value={manualTransaction.amount}
                  onChange={(e) => setManualTransaction({...manualTransaction, amount: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">الوصف</label>
                <input
                  type="text"
                  value={manualTransaction.description}
                  onChange={(e) => setManualTransaction({...manualTransaction, description: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="وصف العملية"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">ملاحظات</label>
                <input
                  type="text"
                  value={manualTransaction.notes}
                  onChange={(e) => setManualTransaction({...manualTransaction, notes: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded"
                  placeholder="ملاحظات إضافية (اختياري)"
                />
              </div>
            </div>
            
            <div className="flex space-x-4 space-x-reverse mt-6">
              <button
                onClick={handleManualTransaction}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                إضافة العملية
              </button>
              <button
                onClick={() => setShowManualForm(false)}
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
    address: 'الحرفيين شارع السوبر جيت',
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
    { key: 'treasury', label: 'الخزينة' },
    { key: 'invoices', label: 'الفواتير' },
    { key: 'work-orders', label: 'أمر شغل' },
    { key: 'pricing', label: 'التسعير' },
    { key: 'users', label: 'إدارة المستخدمين' }
  ];

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      
      // Check if default users exist in database
      const dbUsers = response.data || [];
      const hasElsawy = dbUsers.some(user => user.username === 'Elsawy');
      const hasRoot = dbUsers.some(user => user.username === 'Root');
      
      // Create default users if they don't exist
      if (!hasElsawy) {
        await axios.post(`${API}/users`, {
          username: 'Elsawy',
          password: '100100',
          role: 'admin',
          permissions: allPermissions.map(p => p.key)
        });
      }
      
      if (!hasRoot) {
        await axios.post(`${API}/users`, {
          username: 'Root',
          password: 'master',
          role: 'user',
          permissions: ['dashboard', 'sales', 'inventory', 'deferred', 'expenses', 'treasury', 'work-orders']
        });
      }
      
      // Fetch users again if we created default users
      if (!hasElsawy || !hasRoot) {
        const updatedResponse = await axios.get(`${API}/users`);
        setUsers(updatedResponse.data || []);
      } else {
        setUsers(dbUsers);
      }
      
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fall back to empty array for now
      setUsers([]);
    }
  };

  const addUser = async () => {
    if (!newUser.username || !newUser.password) {
      alert('الرجاء إدخال اسم المستخدم وكلمة المرور');
      return;
    }

    try {
      // Check if username already exists
      if (users.some(user => user.username === newUser.username)) {
        alert('اسم المستخدم موجود بالفعل');
        return;
      }

      // Default permissions based on role
      const defaultPermissions = newUser.role === 'admin' 
        ? allPermissions.map(p => p.key)
        : ['dashboard', 'sales', 'inventory', 'deferred', 'expenses', 'treasury', 'work-orders', 'pricing'];

      // Let backend generate ID and created_at
      const user = {
        username: newUser.username,
        password: newUser.password,
        role: newUser.role,
        permissions: defaultPermissions
      };

      await axios.post(`${API}/users`, user);
      fetchUsers();
      setNewUser({ username: '', password: '', role: 'user' });
      alert('تم إضافة المستخدم بنجاح');
    } catch (error) {
      console.error('Error adding user:', error);
      alert('حدث خطأ في إضافة المستخدم: ' + (error.response?.data?.detail || error.message));
    }
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

  const saveEdit = async () => {
    if (!editForm.username) {
      alert('الرجاء إدخال اسم المستخدم');
      return;
    }

    // Check if username already exists (excluding current user)
    if (users.some(user => user.username === editForm.username && user.id !== editingUser)) {
      alert('اسم المستخدم موجود بالفعل');
      return;
    }

    try {
      // Find current user to preserve their permissions
      const currentUser = users.find(u => u.id === editingUser);
      if (!currentUser) {
        alert('المستخدم غير موجود');
        return;
      }

      // Update user in backend - preserve existing permissions
      const updatedUser = {
        id: editingUser,
        username: editForm.username,
        role: editForm.role,
        password: editForm.password || currentUser.password,
        permissions: currentUser.permissions || [],
        created_at: currentUser.created_at
      };
      
      await axios.put(`${API}/users/${editingUser}`, updatedUser);
      
      // Fetch updated data from database instead of updating local state
      fetchUsers();

      setEditingUser(null);
      setEditForm({ username: '', password: '', role: 'user' });
      alert('تم تحديث المستخدم بنجاح');
    } catch (error) {
      console.error('Error updating user:', error);
      alert('حدث خطأ في تحديث المستخدم: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteUser = async (userId) => {
    if (userId === '1' || userId === '2') {
      alert('لا يمكن حذف المستخدمين الأساسيين');
      return;
    }

    if (!confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return;

    try {
      await axios.delete(`${API}/users/${userId}`);
      fetchUsers();
      alert('تم حذف المستخدم بنجاح');
    } catch (error) {
      console.error('Error deleting user:', error);
      alert('حدث خطأ في حذف المستخدم');
    }
  };

  const resetPassword = async (userId) => {
    const newPassword = prompt('أدخل كلمة المرور الجديدة:');
    if (newPassword && newPassword.trim()) {
      try {
        // Find the user to get their current data
        const user = users.find(u => u.id === userId);
        if (!user) {
          alert('المستخدم غير موجود');
          return;
        }

        // Update password in backend
        const updatedUser = {
          id: user.id,
          username: user.username,
          password: newPassword.trim(),
          role: user.role,
          permissions: user.permissions || [],
          created_at: user.created_at
        };
        
        await axios.put(`${API}/users/${userId}`, updatedUser);
        alert('تم تحديث كلمة المرور بنجاح');
      } catch (error) {
        console.error('Error updating password:', error);
        alert('حدث خطأ في تحديث كلمة المرور: ' + (error.response?.data?.detail || error.message));
      }
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

  const savePermissions = async () => {
    try {
      // Update permissions in backend
      const updatedUser = {
        id: selectedUserPermissions.id,
        username: selectedUserPermissions.username,
        password: selectedUserPermissions.password,
        role: selectedUserPermissions.role,
        permissions: selectedUserPermissions.tempPermissions,
        created_at: selectedUserPermissions.created_at
      };
      
      await axios.put(`${API}/users/${selectedUserPermissions.id}`, updatedUser);
      
      // Fetch updated data from database
      fetchUsers();
      
      setSelectedUserPermissions(null);
      alert('تم تحديث الصلاحيات بنجاح');
    } catch (error) {
      console.error('Error updating permissions:', error);
      alert('حدث خطأ في تحديث الصلاحيات: ' + (error.response?.data?.detail || error.message));
    }
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

// Material Pricing Component
const Pricing = () => {
  const [materialPricings, setMaterialPricings] = useState([]);
  const [editingPricing, setEditingPricing] = useState(null);
  const [newPricing, setNewPricing] = useState({
    material_type: 'NBR',
    inner_diameter: '',
    outer_diameter: '',
    price_per_mm: '',
    manufacturing_cost_client1: '',
    manufacturing_cost_client2: '',
    manufacturing_cost_client3: '',
    notes: ''
  });

  const materialTypes = ['NBR', 'BUR', 'BT', 'VT', 'BOOM'];

  useEffect(() => {
    fetchMaterialPricings();
  }, []);

  const fetchMaterialPricings = async () => {
    try {
      const response = await axios.get(`${API}/material-pricing`);
      setMaterialPricings(response.data);
    } catch (error) {
      console.error('Error fetching material pricings:', error);
    }
  };

  const addMaterialPricing = async () => {
    if (!newPricing.inner_diameter || !newPricing.outer_diameter || !newPricing.price_per_mm) {
      alert('الرجاء إدخال جميع البيانات المطلوبة');
      return;
    }

    try {
      if (editingPricing) {
        // Update existing pricing
        await axios.put(`${API}/material-pricing/${editingPricing}`, {
          ...newPricing,
          inner_diameter: parseFloat(newPricing.inner_diameter),
          outer_diameter: parseFloat(newPricing.outer_diameter),
          price_per_mm: parseFloat(newPricing.price_per_mm),
          manufacturing_cost_client1: parseFloat(newPricing.manufacturing_cost_client1 || 0),
          manufacturing_cost_client2: parseFloat(newPricing.manufacturing_cost_client2 || 0),
          manufacturing_cost_client3: parseFloat(newPricing.manufacturing_cost_client3 || 0)
        });
        alert('تم تحديث التسعيرة بنجاح');
        setEditingPricing(null);
      } else {
        // Add new pricing
        await axios.post(`${API}/material-pricing`, {
          ...newPricing,
          inner_diameter: parseFloat(newPricing.inner_diameter),
          outer_diameter: parseFloat(newPricing.outer_diameter),
          price_per_mm: parseFloat(newPricing.price_per_mm),
          manufacturing_cost_client1: parseFloat(newPricing.manufacturing_cost_client1 || 0),
          manufacturing_cost_client2: parseFloat(newPricing.manufacturing_cost_client2 || 0),
          manufacturing_cost_client3: parseFloat(newPricing.manufacturing_cost_client3 || 0)
        });
        alert('تم إضافة التسعيرة بنجاح');
      }
      
      fetchMaterialPricings();
      setNewPricing({
        material_type: 'NBR',
        inner_diameter: '',
        outer_diameter: '',
        price_per_mm: '',
        manufacturing_cost_client1: '',
        manufacturing_cost_client2: '',
        manufacturing_cost_client3: '',
        notes: ''
      });
    } catch (error) {
      console.error('Error saving material pricing:', error);
      alert('حدث خطأ في حفظ التسعيرة: ' + (error.response?.data?.detail || error.message));
    }
  };

  const editMaterialPricing = (pricing) => {
    setNewPricing({
      material_type: pricing.material_type,
      inner_diameter: pricing.inner_diameter.toString(),
      outer_diameter: pricing.outer_diameter.toString(),
      price_per_mm: pricing.price_per_mm.toString(),
      manufacturing_cost_client1: pricing.manufacturing_cost_client1.toString(),
      manufacturing_cost_client2: pricing.manufacturing_cost_client2.toString(),
      manufacturing_cost_client3: pricing.manufacturing_cost_client3.toString(),
      notes: pricing.notes || ''
    });
    setEditingPricing(pricing.id);
  };

  const deleteMaterialPricing = async (pricingId) => {
    if (!confirm('هل أنت متأكد من حذف هذه التسعيرة؟')) {
      return;
    }

    try {
      await axios.delete(`${API}/material-pricing/${pricingId}`);
      fetchMaterialPricings();
      alert('تم حذف التسعيرة بنجاح');
    } catch (error) {
      console.error('Error deleting material pricing:', error);
      alert('حدث خطأ في حذف التسعيرة: ' + (error.response?.data?.detail || error.message));
    }
  };

  const cancelEdit = () => {
    setEditingPricing(null);
    setNewPricing({
      material_type: 'NBR',
      inner_diameter: '',
      outer_diameter: '',
      price_per_mm: '',
      manufacturing_cost_client1: '',
      manufacturing_cost_client2: '',
      manufacturing_cost_client3: '',
      notes: ''
    });
  };

  return (
    <div className="p-6" dir="rtl">
      <h2 className="text-2xl font-bold text-blue-600 mb-6">💲 إدارة التسعير</h2>
      
      {/* Add/Edit Material Pricing Form */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">
          {editingPricing ? 'تعديل التسعيرة' : 'إضافة تسعيرة جديدة'}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">نوع الخامة</label>
            <select
              value={newPricing.material_type}
              onChange={(e) => setNewPricing({...newPricing, material_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
            >
              {materialTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الداخلي (مم)</label>
            <input
              type="number"
              step="0.1"
              value={newPricing.inner_diameter}
              onChange={(e) => setNewPricing({...newPricing, inner_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="القطر الداخلي"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">القطر الخارجي (مم)</label>
            <input
              type="number"
              step="0.1"
              value={newPricing.outer_diameter}
              onChange={(e) => setNewPricing({...newPricing, outer_diameter: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="القطر الخارجي"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">سعر الملي (ج.م)</label>
            <input
              type="number"
              step="0.01"
              value={newPricing.price_per_mm}
              onChange={(e) => setNewPricing({...newPricing, price_per_mm: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="سعر الملي الواحد"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">تكلفة التصنيع - عميل 1 (ج.م)</label>
            <input
              type="number"
              step="0.01"
              value={newPricing.manufacturing_cost_client1}
              onChange={(e) => setNewPricing({...newPricing, manufacturing_cost_client1: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="تكلفة التصنيع للعميل 1"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">تكلفة التصنيع - عميل 2 (ج.م)</label>
            <input
              type="number"
              step="0.01"
              value={newPricing.manufacturing_cost_client2}
              onChange={(e) => setNewPricing({...newPricing, manufacturing_cost_client2: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="تكلفة التصنيع للعميل 2"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">تكلفة التصنيع - عميل 3 (ج.م)</label>
            <input
              type="number"
              step="0.01"
              value={newPricing.manufacturing_cost_client3}
              onChange={(e) => setNewPricing({...newPricing, manufacturing_cost_client3: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              placeholder="تكلفة التصنيع للعميل 3"
            />
          </div>
          
          <div className="md:col-span-2 lg:col-span-3">
            <label className="block text-sm font-medium mb-1">ملاحظات</label>
            <textarea
              value={newPricing.notes}
              onChange={(e) => setNewPricing({...newPricing, notes: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded"
              rows="2"
              placeholder="ملاحظات إضافية..."
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-4 space-x-reverse mt-4">
          {editingPricing && (
            <button
              onClick={cancelEdit}
              className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
            >
              إلغاء
            </button>
          )}
          <button
            onClick={addMaterialPricing}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            {editingPricing ? 'تحديث التسعيرة' : 'إضافة التسعيرة'}
          </button>
        </div>
      </div>
      
      {/* Material Pricings Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">قائمة التسعيرات</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نوع الخامة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">الأبعاد (داخلي×خارجي)</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">سعر الملي</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عميل 1</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عميل 2</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عميل 3</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ملاحظات</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">العمليات</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {materialPricings.map((pricing, index) => (
                <tr key={pricing.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pricing.material_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.inner_diameter}×{pricing.outer_diameter} مم
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.price_per_mm.toFixed(2)} ج.م
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.manufacturing_cost_client1.toFixed(2)} ج.م
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.manufacturing_cost_client2.toFixed(2)} ج.م
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.manufacturing_cost_client3.toFixed(2)} ج.م
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pricing.notes || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => editMaterialPricing(pricing)}
                      className="text-blue-600 hover:text-blue-900 ml-2"
                    >
                      تعديل
                    </button>
                    <button
                      onClick={() => deleteMaterialPricing(pricing.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              
              {materialPricings.length === 0 && (
                <tr>
                  <td colSpan="8" className="px-6 py-4 text-center text-gray-500">
                    لا توجد تسعيرات مضافة
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('sales'); // Default to sales instead of dashboard
  const { user } = useAuth();

  if (!user) return <Login />;

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': 
        // Only Elsawy can access dashboard
        return user?.username === 'Elsawy' ? <Dashboard /> : <Sales />;
      case 'sales': return <Sales />;
      case 'inventory': return <Inventory />;
      case 'stock': return <Stock />;
      case 'local': return <Local />;
      case 'deferred': return <Deferred />;
      case 'expenses': return <Expenses />;
      case 'revenue': return <Revenue />;
      case 'treasury': return <Treasury />;
      case 'invoices': return <Invoices />;
      case 'work-orders': return <WorkOrders />;
      case 'pricing': return <Pricing />;
      case 'users': return <Users />;
      default: return <Sales />; // Default to sales instead of dashboard
    }
  };

  return (
    <div className="flex h-screen bg-gray-50" dir="rtl">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="flex-1 overflow-y-auto bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="p-6">
          {renderPage()}
        </div>
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