#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



user_problem_statement: "بناء نظام إدارة متكامل لشركة ماستر سيل لتصنيع وتوريد أويل سيل باللغة العربية"

backend:
  - task: "Auth endpoints - تسجيل الدخول"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "تم بناء نظام المصادقة مع المستخدمين المحددين مسبقاً (Elsawy/100100, Root/master)"

  - task: "Dashboard API - إحصائيات لوحة التحكم"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "API يجلب إجمالي المبيعات والمصروفات والأرباح وعدد الفواتير والعملاء"

  - task: "Customer management APIs"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم بناء APIs لإدارة العملاء - يحتاج اختبار"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار جميع APIs العملاء بنجاح - إنشاء 4 عملاء بأسماء عربية، استرجاع جميع العملاء، استرجاع عميل محدد. جميع العمليات تعمل بشكل مثالي."

  - task: "Raw materials inventory APIs"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "تم بناء APIs لإدارة المواد الخام مع المقاسات والخامات المختلفة"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار جميع APIs المواد الخام بنجاح - إنشاء 5 أنواع مختلفة من الخامات (NBR, BUR, BT, VT, BOOM) بمقاسات متنوعة، استرجاع جميع المواد. تحديث المخزون يعمل بشكل صحيح عند إنشاء الفواتير."

  - task: "Compatibility check API"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "API لفحص توافق الخامات مع مواصفات الأويل سيل المطلوبة"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار API فحص التوافق بنجاح بعد إصلاح مشكلة MongoDB ObjectId. تم اختبار جميع أنواع الأويل سيل (RSL, RS, RSE, B17, B3) ومنطق التوافق يعمل بشكل صحيح بناءً على المقاسات."

  - task: "Invoice management APIs"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "APIs شاملة لإدارة الفواتير مع تحديث المخزون التلقائي"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار جميع APIs الفواتير بنجاح - إنشاء 3 فواتير بطرق دفع مختلفة (نقدي، آجل، فودافون كاش)، استرجاع جميع الفواتير، استرجاع فاتورة محددة. تحديث المخزون التلقائي يعمل بشكل صحيح."

  - task: "Payment tracking APIs"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "نظام لتتبع المدفوعات والدفع الجزئي والآجل"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار جميع APIs المدفوعات بنجاح - إنشاء دفعات جزئية بطرق مختلفة (نقدي، فودافون كاش)، استرجاع جميع المدفوعات. تحديث حالة الفواتير يعمل بشكل صحيح."

  - task: "Expense management APIs"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "APIs لإدارة مصروفات الشركة بفئات مختلفة"
      - working: true
        agent: "testing"
        comment: "✅ تم اختبار جميع APIs المصروفات بنجاح - إنشاء 5 مصروفات بفئات مختلفة (خامات، رواتب، كهرباء، صيانة، أخرى)، استرجاع جميع المصروفات. جميع العمليات تعمل بشكل مثالي."

frontend:
  - task: "Authentication system"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "نظام تسجيل دخول باللغة العربية مع Context للمصادقة يعمل بشكل مثالي"

  - task: "Navigation and layout"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "شريط تنقل عربي مع صلاحيات مختلفة للمستخدمين (إدارة/عادي)"

  - task: "Dashboard component"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "لوحة تحكم تعرض الإحصائيات بشكل جميل باللغة العربية"

  - task: "Sales interface"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "واجهة مبيعات شاملة مع اختيار العملاء وإدخال المنتجات وفحص التوافق"

  - task: "Other page components (placeholders)"
    implemented: true
    working: true
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "صفحات أساسية لجميع الأقسام (مخزون، آجل، مصروفات، إيرادات، فواتير، أمر شغل، مستخدمين)"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Backend APIs testing completed successfully"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "تم بناء النظام الأساسي بنجاح. الواجهة تعمل بشكل ممتاز مع نظام المصادقة ولوحة التحكم وصفحة المبيعات. يحتاج اختبار APIs الخلفية للتأكد من صحة العمل مع قاعدة البيانات."