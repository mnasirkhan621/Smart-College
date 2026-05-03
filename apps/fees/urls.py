from django.urls import path

from . import views


app_name = "fees"

urlpatterns = [
    path("", views.FeeHomeView.as_view(), name="home"),
    path("categories/", views.FeeCategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.FeeCategoryCreateView.as_view(), name="category_create"),
    path("structures/", views.FeeStructureListView.as_view(), name="structure_list"),
    path("structures/create/", views.FeeStructureCreateView.as_view(), name="structure_create"),
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/create/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("payments/create/", views.PaymentCreateView.as_view(), name="payment_create"),
    path("receipts/<int:pk>/", views.ReceiptDetailView.as_view(), name="receipt_detail"),
    path("pending-dues/", views.PendingDuesView.as_view(), name="pending_dues"),
    path("my-fees/", views.StudentFeeView.as_view(), name="student_fees"),
]
