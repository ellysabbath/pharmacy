from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.conf import settings
import secrets
from tinymce import models as tinymce_models
import phonenumbers
from phonenumbers import phonenumberutil


# Helper function to format the mobile number
def format_mobile_number(mobile_number, region='TZ'):
    try:
        # Parse the mobile number with the specified region (defaulting to 'TZ' for Tanzania)
        phone_number = phonenumbers.parse(mobile_number, region)
        
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError("Invalid phone number")
        
        # Return the phone number in E.164 format (e.g., +255742575555 for Tanzania)
        return phonenumbers.format_number(phone_number, phonenumberutil.PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValueError("Invalid phone number format")

# Custom user model to include email and mobile number
class CustomUser(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('normal', 'Normal'),
    ]
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, default='')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True) 
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def clean_mobile_number(self):
        # Format the mobile number before saving it
        if self.mobile_number:
            self.mobile_number = format_mobile_number(self.mobile_number)

# OTP Token model to store OTP information
class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))  # Modify this later
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username




# *************************medicine******************************
class Medicine(models.Model):
    ALERT_CHOICES = [
        ('Low Stock', '🔴 Low Stock'),
        ('Near Expiry', '⏳ Near Expiry'),
        ('OK', '✅ OK'),
    ]
    pharmacy_name=models.CharField(max_length=100, default='')
    medicine_name = models.CharField(max_length=100)
    stock = models.CharField(max_length=100)
    expiry_date = models.DateField()
    alert_status = models.CharField(max_length=20, choices=ALERT_CHOICES)

    def __str__(self):
        return self.medicine_name
    



    
from django.db import models
from django.utils import timezone

class SalesEntry(models.Model):
    pharmacy_name = models.CharField(max_length=255, null=False, default='pharmacy')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    daily_sales = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    day = models.PositiveIntegerField(editable=False, null=True)
    week = models.PositiveIntegerField(editable=False, null=True)
    month = models.PositiveIntegerField(editable=False, null=True)  # changed here

    date = models.DateField(default=timezone.now)  # date only

    def save(self, *args, **kwargs):
        now = self.date if self.date else timezone.now().date()
        self.day = now.day
        self.week = now.isocalendar()[1]
        self.month = now.month  # integer 1-12

        self.total = (self.unit_price * self.quantity) - (self.discount + self.tax)
        self.daily_sales = self.unit_price * self.quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pharmacy_name} - {self.product_name} ({self.date})"

class cartInfo(models.Model):
    pharmacy_name = models.CharField(max_length=255)
    cart_product = models.CharField(max_length=255)
    cart_quantity = models.PositiveIntegerField()
    cart_price = models.DecimalField(max_digits=10, decimal_places=2)
    cart_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    


# ***************************sales summary******************************
from django.db import models
from django.utils import timezone
import random

class SalesSummary(models.Model):
    daily_sales = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_sales = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_sales = models.DecimalField(max_digits=10, decimal_places=2)

    # Removed `day` field as requested
    week = models.PositiveIntegerField(editable=False)
    month = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        now = timezone.now()
        self.week = now.isocalendar()[1]
        self.month = now.month
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sales Summary for Week {self.week}, Month {self.month}"


class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255)

    # Change day to PositiveIntegerField since you want day number
    day = models.PositiveIntegerField(editable=False, null=True)
    month = models.PositiveIntegerField(editable=False, null=True)

    def save(self, *args, **kwargs):
        now = timezone.now().date()
        self.day = now.day
        self.month = now.month
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supplier_name} ({self.company_name})"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('Received', 'Received'),
        ('Pending', 'Pending'),
    ]

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    supplier_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    day = models.PositiveIntegerField(editable=False, null=True)
    month = models.PositiveIntegerField(editable=False, null=True)

def save(self, *args, **kwargs):
    current_date = timezone.now().date()
    self.day = current_date.day
    self.month = current_date.month

    if not self.pk and not self.order_id:
        self.order_id = self._generate_unique_order_id()

    super().save(*args, **kwargs)


    super().save(*args, **kwargs)



    def _generate_unique_order_id(self):
        while True:
            number = random.randint(0, 99999)
            new_id = f"PO-{number:05d}"  # e.g. PO-00123
            if not PurchaseOrder.objects.filter(order_id=new_id).exists():
                return new_id
            




    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self._generate_unique_order_id()

        now = self.day if self.day else timezone.now().date()
        self.day = now.day
        self.month = now.month
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.supplier_name}"
    


import datetime
class IncomingStock(models.Model):
    medicine = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    expected_date = models.DateField(default=timezone.now)
    supplier_name = models.CharField(max_length=255)

    day = models.PositiveIntegerField(editable=False, null=True)
    month = models.PositiveIntegerField(editable=False, null=True)

    def save(self, *args, **kwargs):
        # Convert expected_date to a date object if it's a string
        if isinstance(self.expected_date, str):
            self.expected_date = datetime.datetime.strptime(self.expected_date, '%Y-%m-%d').date()

        now = self.expected_date if self.expected_date else timezone.now().date()
        self.day = now.day
        self.month = now.month
        super().save(*args, **kwargs)



class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    contact = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    pharmacy_name = models.CharField(max_length=50, default='Main Branch')


    def __str__(self):
        return self.full_name


class PurchaseHistory(models.Model):
    expected_date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    medicine = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    pharmacy_name = models.CharField(max_length=50, default='Main Branch')

    
    def save(self, *args, **kwargs):
        # Convert expected_date to a date object if it's a string
        if isinstance(self.expected_date, str):
            self.expected_date = datetime.datetime.strptime(self.expected_date, '%Y-%m-%d').date()

        now = self.expected_date if self.expected_date else timezone.now().date()
        self.day = now.day
        self.month = now.month
        super().save(*args, **kwargs)

        # ***********************reporting and analysis******************************
        # 1. Regulatory & Compliance Reporting
class RegulatoryReport(models.Model):
    report_type = models.CharField(max_length=255)
    description = models.TextField()
    frequency = models.CharField(max_length=100)
    submitted_to = models.CharField(max_length=255)
    compliance_notes = models.TextField(blank=True)

    def __str__(self):
        return self.report_type

# 2. Operational Reporting
class OperationalReport(models.Model):
    metric = models.CharField(max_length=255)
    description = models.TextField()
    reporting_period = models.CharField(max_length=100)
    target_kpi = models.CharField(max_length=255)

    def __str__(self):
        return self.metric

# 3. Clinical & Patient Outcome Reporting
class ClinicalReport(models.Model):
    clinical_metric = models.CharField(max_length=255)
    description = models.TextField()
    patient_impact = models.TextField()
    data_source = models.CharField(max_length=255)

    def __str__(self):
        return self.clinical_metric

# 4. Tools & Data Integration
class ToolIntegration(models.Model):
    tool_system = models.CharField(max_length=255)
    purpose = models.TextField()
    example_vendors = models.CharField(max_length=255)
    integration_notes = models.TextField()

    def __str__(self):
        return self.tool_system
    

# ***********************end****************************
class Drug(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class LowStockAlert(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='low_stock_alerts', default='')
    remaining_units = models.PositiveIntegerField()

    def __str__(self):
        return f"Low stock for {self.medicine.medicine_name}: {self.remaining_units}"


class ExpiryAlert(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='expiry_alerts', null=True, default='')

    days_to_expiry = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.medicine.medicine_name} expires in {self.days_to_expiry} days"


class Suplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class PendingOrder(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=50)  # e.g., "Pending Delivery", "Awaiting Confirmation"

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else 'Unknown'
        return f"Order {self.order_id} from {supplier_name}"