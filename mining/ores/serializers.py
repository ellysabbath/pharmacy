from rest_framework import serializers

from rest_framework import serializers
from .models import Medicine,SalesEntry,cartInfo,SalesSummary

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class SalesEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateField() 
    class Meta:
        model = SalesEntry
        fields = '__all__'

class cartInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = cartInfo
        fields = '__all__'


class SalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesSummary
        fields = '__all__'



from rest_framework import serializers
from .models import Supplier, PurchaseOrder, IncomingStock

# ----------------------
# Supplier Serializer
# ----------------------
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'  # Includes all model fields


# ----------------------
# Purchase Order Serializer
# ----------------------
class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'  # Includes all model fields


# ----------------------
# Incoming Stock Serializer
# ----------------------
class IncomingStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomingStock
        fields = '__all__'  # Includes all model fields


from .models import Customer, PurchaseHistory

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class PurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseHistory
        fields = '__all__'
from .models import RegulatoryReport, OperationalReport, ClinicalReport, ToolIntegration

class RegulatoryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryReport
        fields = '__all__'

class OperationalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalReport
        fields = '__all__'

class ClinicalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalReport
        fields = '__all__'

class ToolIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolIntegration
        fields = '__all__'


# **************************end***********************
from rest_framework import serializers
from .models import Drug, LowStockAlert, ExpiryAlert, Suplier, PendingOrder

class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ['id', 'name', 'description', 'unit_price', 'quantity_in_stock', 'expiry_date']

class LowStockAlertSerializer(serializers.ModelSerializer):
    drug = DrugSerializer(read_only=True)
    drug_id = serializers.PrimaryKeyRelatedField(
        queryset=Drug.objects.all(), source='drug', write_only=True
    )

    class Meta:
        model = LowStockAlert
        fields = ['id', 'drug', 'drug_id', 'remaining_units']

class ExpiryAlertSerializer(serializers.ModelSerializer):
    drug = DrugSerializer(read_only=True)
    drug_id = serializers.PrimaryKeyRelatedField(
        queryset=Drug.objects.all(), source='drug', write_only=True
    )

    class Meta:
        model = ExpiryAlert
        fields = ['id', 'drug', 'drug_id', 'days_to_expiry']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suplier
        fields = ['id', 'name', 'contact_info']

class PendingOrderSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True
    )

    class Meta:
        model = PendingOrder
        fields = ['id', 'order_id', 'supplier', 'supplier_id', 'status']


# *****************************admin*******************************
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'mobile_number', 'role']
        read_only_fields = []  # ✅ allow role to be writable

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            mobile_number=validated_data.get('mobile_number', ''),
            role=validated_data['role'],
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
