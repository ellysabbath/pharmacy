from django.urls import path
from . import views  
from .views import MedicineListCreateAPIView,profile,SalesSummaryDetailAPIView,SalesSummaryListCreateAPIView,CartDetailAPIView,CartListCreateAPIView, MedicineDetailAPIView,SalesEntryListCreateAPIView, SalesEntryDetailAPIView

from django.contrib.auth import views as auth_views
from .views import (
    SupplierListCreateAPIView, SupplierDetailAPIView,
    PurchaseOrderListCreateAPIView, PurchaseOrderDetailAPIView,
    IncomingStockListCreateAPIView, IncomingStockDetailAPIView,
    CustomerListCreateAPIView,
    CustomerDetailAPIView,
    PurchaseHistoryListCreateAPIView,
    PurchaseHistoryDetailAPIView,
    RegulatoryReportListCreateAPIView, RegulatoryReportDetailAPIView,
    OperationalReportListCreateAPIView, OperationalReportDetailAPIView,
    ClinicalReportListCreateAPIView, ClinicalReportDetailAPIView,
    ToolIntegrationListCreateAPIView, ToolIntegrationDetailAPIView,
    DrugListCreateAPIView, DrugDetailAPIView,
    LowStockAlertListCreateAPIView, LowStockAlertDetailAPIView,
    ExpiryAlertListCreateAPIView, ExpiryAlertDetailAPIView,
    SupplierListCreateAPIView, SupplierDetailAPIView,
    PendingOrderListCreateAPIView, PendingOrderDetailAPIView,
    UserListCreateAPIView, UserDetailAPIView
)

urlpatterns = [
    path('',views.landing, name='landing'),
    path('signup/', views.SignUp, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('verify-email/<str:username>/', views.Verify_email, name='verify-email'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),
    path('tucasa/', views.index, name='index'),
    path('request-reset-password/', views.request_reset_password, name='request-reset-password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset-password'),
    path('logout/', views.logout_view, name='logout'),  # Add the logout URL
    path('send-otp/', views.send_sms, name='send_sms'),
    path('status-callback/', views.message_status_callback, name='message_status_callback'),
    path('myprofile/',views.profile,name="profile"),

    # ######################## internal ###################
    path('pharmacy/home/', views.Dashboard, name="user-dashboard"),
   


    path('pharmacy/medicine/', views.communication, name="communication"),
    path('pharmacy/sales/', views.medicalMissionary, name="medicalMissionary"),
    path('pharmacy/supplier/', views.mhazini, name="mhazini"),
  
    path('pharmacy/customer/', views.udomZoneAllMembers, name="udomzoneallmembers"),
    path('pharmacy/reporting/', views.ZoneHistorical, name="History"),
 
    path('pharmacy/notifications/', views.ventures, name="ventures"),
  

    # ***********************forms*********************************
    path('pharmacy/customer/create/', views.customerform, name="customer"),

    path('pharmacy/medicine/create/', views.medicineform, name="medicine"),
    path('pharmacy/notifications/create/', views.notificationsform, name="notifications"),
    path('pharmacy/reporting/create/', views.reportingform, name="reporting"),
    path('pharmacy/sales/create/', views.salesform, name="sales"),
    path('pharmacy/supplier/create/', views.supplierform, name="suplier"),
  

#   ******************************8logics*********************************
    path('api/medicines/', MedicineListCreateAPIView.as_view(), name='medicine-list-create'),
    path('api/medicines/<int:pk>/', MedicineDetailAPIView.as_view(), name='medicine-detail'),


    path('api/sales/', SalesEntryListCreateAPIView.as_view(), name='sales-list-create'),
    path('api/sales/<int:pk>/', SalesEntryDetailAPIView.as_view(), name='sales-detail'),


    path('api/cart/', CartListCreateAPIView.as_view(), name='cart-list-create'),
    path('api/cart/<int:pk>/', CartDetailAPIView.as_view(), name='cart-detail'),

    path('sales/', SalesSummaryListCreateAPIView.as_view(), name='sales-list-create'),
    path('sales/<int:pk>/', SalesSummaryDetailAPIView.as_view(), name='sales-detail'),


        # Supplier Endpoints
    path('api/suppliers/', SupplierListCreateAPIView.as_view(), name='supplier-list-create'),
    path('api/suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),

    # Purchase Order Endpoints
    path('api/purchase-orders/', PurchaseOrderListCreateAPIView.as_view(), name='purchaseorder-list-create'),
    path('api/purchase-orders/<int:pk>/', PurchaseOrderDetailAPIView.as_view(), name='purchaseorder-detail'),

    # Incoming Stock Endpoints
    path('api/incoming-stock/', IncomingStockListCreateAPIView.as_view(), name='incomingstock-list-create'),
    path('api/incoming-stock/<int:pk>/', IncomingStockDetailAPIView.as_view(), name='incomingstock-detail'),

    path('api/customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('api/customers/<int:pk>/', CustomerDetailAPIView.as_view(), name='customer-detail'),
    path('api/purchase-history/', PurchaseHistoryListCreateAPIView.as_view(), name='purchase-history-list-create'),
    path('api/purchase-history/<int:pk>/', PurchaseHistoryDetailAPIView.as_view(), name='purchase-history-detail'),


    # ****************************reporting and analysis*********************************
    path('api/regulatory/', RegulatoryReportListCreateAPIView.as_view()),
    path('api/regulatory/<int:pk>/', RegulatoryReportDetailAPIView.as_view()),

    path('api/operational/', OperationalReportListCreateAPIView.as_view()),
    path('api/operational/<int:pk>/', OperationalReportDetailAPIView.as_view()),

    path('api/clinical/', ClinicalReportListCreateAPIView.as_view()),
    path('api/clinical/<int:pk>/', ClinicalReportDetailAPIView.as_view()),

    path('api/tools/', ToolIntegrationListCreateAPIView.as_view()),
    path('api/tools/<int:pk>/', ToolIntegrationDetailAPIView.as_view()),
    
    # ****************************end*****************************
        # Drugs
    path('drugs/', DrugListCreateAPIView.as_view(), name='drug-list-create'),
    path('drugs/<int:pk>/', DrugDetailAPIView.as_view(), name='drug-detail'),

    # Low Stock Alerts
    path('low-stock-alerts/', LowStockAlertListCreateAPIView.as_view(), name='low-stock-alert-list-create'),
    path('low-stock-alerts/<int:pk>/', LowStockAlertDetailAPIView.as_view(), name='low-stock-alert-detail'),

    # Expiry Alerts
    path('expiry-alerts/', ExpiryAlertListCreateAPIView.as_view(), name='expiry-alert-list-create'),
    path('expiry-alerts/<int:pk>/', ExpiryAlertDetailAPIView.as_view(), name='expiry-alert-detail'),

    # Suppliers
    path('suppliers/', SupplierListCreateAPIView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),

    # Pending Orders
    path('pending-orders/', PendingOrderListCreateAPIView.as_view(), name='pending-order-list-create'),
    path('pending-orders/<int:pk>/', PendingOrderDetailAPIView.as_view(), name='pending-order-detail'),

    # ************************Admin********************************
    path('users/', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
]