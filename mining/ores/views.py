from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from .models import OtpToken

from django.urls import reverse
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from django.contrib import messages
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
import secrets
import json
import logging
import string
import phonenumbers
from twilio.rest import Client  # Twilio to send SMS
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import FileSystemStorage






# Twilio configuration (replace with your actual credentials)
# TWILIO_PHONE_NUMBER = '+12766008030'
# TWILIO_SID = 'AC380fd733caa676f79347b1ed86b0be0f'
# TWILIO_AUTH_TOKEN = 'cbef6c8a3cce29de9593b1526ba2a377'

# Function to generate and send OTP to mobile number via Twilio
# Set up logging to capture errors and debug information
# logger = logging.getLogger(__name__)

# def send_otp_to_mobile(mobile_number, otp_code):
#     try:
#         # Ensure phone number is in E.164 format
#         parsed_number = phonenumbers.parse(mobile_number, "TZ")  # Replace "TZ" with correct region code
#         if not phonenumbers.is_valid_number(parsed_number):
#             raise ValueError(f"Invalid phone number: {mobile_number}")
        
#         formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

#         # Log the formatted phone number for debugging
#         logger.debug(f"Sending OTP to mobile number: {formatted_number}")

#         # Initialize Twilio client
#         client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

#         # Send OTP via SMS
#         message = client.messages.create(
#             body=f"Your OTP is: {otp_code}. It will expire in 5 minutes.",
#             from_=settings.TWILIO_PHONE_NUMBER,
#             to=formatted_number
#         )

#         # Log the message SID to confirm the message was sent
#         logger.debug(f"Message sent successfully. SID: {message.sid}")
#         return message.sid  # Return the message SID for tracking if needed

#     except Exception as e:
#         # Log the error
#         logger.error(f"Error sending OTP to mobile number {mobile_number}: {e}")
#         raise e

# Function to send OTP to email

def send_otp_to_email(email, otp_code):
    subject = "Email Verification"
    message = f"Hi there,\nHere is your OTP: {otp_code}\nIt expires in 5 minutes."
    sender = "iyumbusda@gmail.com"
    receiver = [email]
    send_mail(subject, message, sender, receiver, fail_silently=False)

# Create your views here.
@login_required
def index(request):
    return render(request, "index.html")

def SignUp(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Generate OTP (6-digit random number)
            otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))

            # Create OTP record for the user
            otp = OtpToken.objects.create(
                user=user,
                otp_code=otp_code,
                otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )

            # Send OTP to user's email
            send_otp_to_email(user.email, otp_code)

            # Send OTP to user's mobile number if available
            # Uncomment the next line if you have a mobile number for the user
            # if user.mobile_number:
            #     send_otp_to_mobile(user.mobile_number, otp_code)

            # Now send the success message
            messages.success(request, f"Account created successfully! An OTP was sent to your email and mobile number. OTP: {otp_code}")

            return redirect("verify-email", username=user.username)
        else:
            messages.error(request, "There was an error with your form. Please try again.")
    
    context = {"form": form}
    return render(request, "signup.html", context)

def Verify_email(request, username):
    try:
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("signup")

    user_otp = OtpToken.objects.filter(user=user).last()

    if not user_otp:
        messages.error(request, "No OTP found. Please request a new one.")
        return redirect("resend-otp")

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code')

        if user_otp.otp_code == entered_otp:
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully! You can now login.")
                return redirect("signin")
            else:
                messages.warning(request, "The OTP has expired. Please request a new one.")
                return redirect("resend-otp")
        else:
            messages.warning(request, "Invalid OTP. Please try again.")
            return redirect(reverse("verify-email", kwargs={"username": user.username}))

    context = {'username': username, 'otp': user_otp}
    return render(request, "verify_token.html", context)

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST.get("otp_email")
        
        try:
            user = get_user_model().objects.get(email=user_email)

            otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))  # Generate new OTP

            otp = OtpToken.objects.create(
                user=user,
                otp_code=otp_code,
                otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )

            # Send OTP via email
            send_otp_to_email(user.email, otp_code)

            # Send OTP via mobile if available
            # if user.mobile_number:
            #     send_otp_to_mobile(user.mobile_number, otp_code)

            messages.success(request, f"A new OTP has been sent to your email and mobile number. OTP: {otp_code}")

            return redirect("verify-email", username=user.username)

        except get_user_model().DoesNotExist:
            messages.warning(request, "This email doesn't exist in the records.")
            return redirect("resend-otp")

    return render(request, "resend_otp.html")

def signin(request):
    if request.user.is_authenticated:
        return redirect("user-dashboard")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("user-dashboard")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            print(messages.get_messages(request))  # This will print the messages to the console
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('signin')

# Password reset views (step 1)
def request_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = get_user_model().objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            subject = "Password Reset Request"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'uid': uid,
                'token': token,
            })
            send_mail(subject, message, 'no-reply@yourdomain.com', [email], fail_silently=False)
            
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect("signin")
        
        except get_user_model().DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return redirect("request-reset-password")

    return render(request, "request_reset_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("signin")
            
            return render(request, "reset_password.html", {'uid': uidb64, 'token': token})
        else:
            messages.error(request, "The password reset link is invalid or has expired.")
            return redirect("signin")
    
    except Exception as e:
        messages.error(request, "There was an error processing your request. Please try again.")
        return redirect("signin")

def send_password_reset_email(user):
    uid = urlsafe_base64_encode(user.pk.encode())
    token = default_token_generator.make_token(user)
    reset_url = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"

    subject = "Password Reset Request"
    html_message = render_to_string('password_reset_email.html', {
        'user': user,
        'uid': uid,
        'token': token,
    })
    plain_message = f"Hi {user.username},\n\nWe received a request to reset your password. Please click the link below to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."

    send_mail(
        subject,
        plain_message,
        'iyumbusda@gmail.com',
        [user.email],
        html_message=html_message,
    )



# Your Twilio account SID and Auth token
account_sid = 'AC380fd733caa676f79347b1ed86b0be0f'
auth_token = 'cbef6c8a3cce29de9593b1526ba2a377'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def send_sms(request):
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body="Your OTP code is 123456",
            from_='+12766008030',  # Your Twilio phone number
            to='+255742578691'  # The recipient's phone number
        )
        
        # After sending the message, fetch the message status
        message_sid = message.sid  # Get the SID of the sent message
        message_status = client.messages(message_sid).fetch().status  # Fetch the message and check its status

        # Log the message status for debugging purposes
        logging.debug(f"Message SID: {message_sid}, Message Status: {message_status}")

        # Respond with the message status
        return HttpResponse(f"Message sent successfully: {message.sid}. Status: {message_status}")

    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return HttpResponse(f"Failed to send message: {e}")
    

    # This view will handle the callback from Twilio
def message_status_callback(request):
    message_sid = request.GET.get('MessageSid')
    message_status = request.GET.get('MessageStatus')
    logging.info(f"Message SID: {message_sid}, Status: {message_status}")

    # You can add your logic here to update your database or notify the user
    # For now, we'll just return a response to acknowledge receipt
    return JsonResponse({'status': 'Received', 'MessageSid': message_sid, 'MessageStatus': message_status})

@login_required
def Dashboard(request):
    return render(request, "registration/home.html")
@login_required
def mhazini_view(request):
    return render(request, "registration/medicine.html")


def landing(request):
    return render(request, "landing.html")

@login_required
def mhazini(request):
    return render(request, "registration/sales.html")


@login_required
def communication(request):
    return render(request, "registration/medicine.html")
@login_required
def medicalMissionary(request):
    return render(request, "registration/customer.html")

@login_required
def profile(request):
    return render(request, "registration/profile.html")

@login_required
def udomZoneAllMembers(request):
    return render(request, "registration/reporting.html")
@login_required
def ventures(request):
    return render(request, "registration/supplier.html")
@login_required
def ZoneHistorical(request):
    return render(request, "registration/notifications.html")

@login_required
def customerform(request):
    return render(request, "registration/customerform.html")

@login_required
def medicineform(request):
    return render(request, "registration/medicineform.html")
@login_required
def notificationsform(request):
    return render(request, "registration/notificationsform.html")

@login_required
def reportingform(request):
    return render(request, "registration/reportingform.html")

@login_required
def salesform(request):
    return render(request, "registration/salesform.html")
@login_required
def supplierform(request):
    return render(request, "registration/supplierform.html")



# *************************************8logical pharmacy***********************************
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Medicine
from .serializers import MedicineSerializer

class MedicineListCreateAPIView(APIView):
    def get(self, request):
        medicines = Medicine.objects.all().order_by('-id')
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicineDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Medicine, pk=pk)

    def get(self, request, pk):
        medicine = self.get_object(pk)
        serializer = MedicineSerializer(medicine)
        return Response(serializer.data)

    def put(self, request, pk):
        medicine = self.get_object(pk)
        serializer = MedicineSerializer(medicine, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        medicine = self.get_object(pk)
        medicine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# **********************************sales*************************************
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from .models import SalesEntry,cartInfo,SalesSummary
from .serializers import SalesEntrySerializer,cartInfoSerializer,SalesSummarySerializer

class SalesEntryListCreateAPIView(APIView):
    def get(self, request):
        sales = SalesEntry.objects.all().order_by('-id')
        today = timezone.now().date()
        week_start = today - timedelta(days=6)
        month_start = today.replace(day=1)

        enriched_data = []

        for sale in sales:
            weekly_total = SalesEntry.objects.filter(
                pharmacy_name=sale.pharmacy_name,
                date__range=(week_start, today)
            ).aggregate(Sum('daily_sales'))['daily_sales__sum'] or 0

            monthly_total = SalesEntry.objects.filter(
                pharmacy_name=sale.pharmacy_name,
                date__gte=month_start
            ).aggregate(Sum('daily_sales'))['daily_sales__sum'] or 0

            serialized = SalesEntrySerializer(sale).data
            serialized['weekly_sales'] = float(weekly_total)
            serialized['monthly_sales'] = float(monthly_total)
            enriched_data.append(serialized)

        return Response(enriched_data)

    def post(self, request):
        serializer = SalesEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalesEntryDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(SalesEntry, pk=pk)

    def get(self, request, pk):
        sale = self.get_object(pk)
        serializer = SalesEntrySerializer(sale)
        return Response(serializer.data)

    def put(self, request, pk):
        sale = self.get_object(pk)
        serializer = SalesEntrySerializer(sale, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sale = self.get_object(pk)
        sale.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ***************************************cart info********************************************

class CartListCreateAPIView(APIView):
    def get(self, request):
        cart = cartInfo.objects.all().order_by('-id')
        serializer = cartInfoSerializer(cart, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = cartInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(cartInfo, pk=pk)

    def get(self, request, pk):
        sale = self.get_object(pk)
        serializer = cartInfoSerializer(sale)
        return Response(serializer.data)

    def put(self, request, pk):
        sale = self.get_object(pk)
        serializer = cartInfoSerializer(sale, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sale = self.get_object(pk)
        sale.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# *************************************sales summary*********************************


class SalesSummaryListCreateAPIView(APIView):
    def get(self, request):
        summaries = SalesSummary.objects.all().order_by('-id')
        serializer = SalesSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SalesSummarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # auto-generates day, week, and month
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SalesSummaryDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(SalesSummary, pk=pk)

    def get(self, request, pk):
        summary = self.get_object(pk)
        serializer = SalesSummarySerializer(summary)
        return Response(serializer.data)

    def put(self, request, pk):
        summary = self.get_object(pk)
        serializer = SalesSummarySerializer(summary, data=request.data)
        if serializer.is_valid():
            serializer.save()  # will update week/month/day if changed
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        summary = self.get_object(pk)
        summary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# *****************************purchase view***************************************
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Supplier, PurchaseOrder, IncomingStock
from .serializers import SupplierSerializer, PurchaseOrderSerializer, IncomingStockSerializer


# 🌿 Supplier Views
class SupplierListCreateAPIView(APIView):
    def get(self, request):
        suppliers = Supplier.objects.all().order_by('-id')
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Supplier, pk=pk)

    def get(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)

    def put(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        supplier = self.get_object(pk)
        supplier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 📦 PurchaseOrder Views
class PurchaseOrderListCreateAPIView(APIView):
    def get(self, request):
        orders = PurchaseOrder.objects.all().order_by('-id')
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(PurchaseOrder, pk=pk)

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        serializer = PurchaseOrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 🚚 IncomingStock Views
class IncomingStockListCreateAPIView(APIView):
    def get(self, request):
        stocks = IncomingStock.objects.all().order_by('-id')
        serializer = IncomingStockSerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IncomingStockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncomingStockDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(IncomingStock, pk=pk)

    def get(self, request, pk):
        stock = self.get_object(pk)
        serializer = IncomingStockSerializer(stock)
        return Response(serializer.data)

    def put(self, request, pk):
        stock = self.get_object(pk)
        serializer = IncomingStockSerializer(stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        stock = self.get_object(pk)
        stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

from .models import Customer, PurchaseHistory
from .serializers import CustomerSerializer, PurchaseHistorySerializer


class CustomerListCreateAPIView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Customer, pk=pk)

    def get(self, request, pk):
        customer = self.get_object(pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = self.get_object(pk)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = self.get_object(pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PurchaseHistoryListCreateAPIView(APIView):
    def get(self, request):
        purchases = PurchaseHistory.objects.all()
        serializer = PurchaseHistorySerializer(purchases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseHistoryDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(PurchaseHistory, pk=pk)

    def get(self, request, pk):
        history = self.get_object(pk)
        serializer = PurchaseHistorySerializer(history)
        return Response(serializer.data)

    def put(self, request, pk):
        history = self.get_object(pk)
        serializer = PurchaseHistorySerializer(history, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        history = self.get_object(pk)
        history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



# ******************************regulatory report APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import RegulatoryReport
from .serializers import RegulatoryReportSerializer

class RegulatoryReportListCreateAPIView(APIView):
    def get(self, request):
        reports = RegulatoryReport.objects.all().order_by('-id')
        serializer = RegulatoryReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegulatoryReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegulatoryReportDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(RegulatoryReport, pk=pk)

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = RegulatoryReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = RegulatoryReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ******************************operationalreportAPIView ***************************
from .models import OperationalReport
from .serializers import OperationalReportSerializer

class OperationalReportListCreateAPIView(APIView):
    def get(self, request):
        reports = OperationalReport.objects.all().order_by('-id')
        serializer = OperationalReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OperationalReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OperationalReportDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(OperationalReport, pk=pk)

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = OperationalReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = OperationalReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ****************************888clinical report view*********************************
from .models import ClinicalReport
from .serializers import ClinicalReportSerializer

class ClinicalReportListCreateAPIView(APIView):
    def get(self, request):
        reports = ClinicalReport.objects.all().order_by('-id')
        serializer = ClinicalReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClinicalReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClinicalReportDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(ClinicalReport, pk=pk)

    def get(self, request, pk):
        report = self.get_object(pk)
        serializer = ClinicalReportSerializer(report)
        return Response(serializer.data)

    def put(self, request, pk):
        report = self.get_object(pk)
        serializer = ClinicalReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# *****************************************tol integration view*********************************
from .models import ToolIntegration
from .serializers import ToolIntegrationSerializer

class ToolIntegrationListCreateAPIView(APIView):
    def get(self, request):
        tools = ToolIntegration.objects.all().order_by('-id')
        serializer = ToolIntegrationSerializer(tools, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ToolIntegrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToolIntegrationDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(ToolIntegration, pk=pk)

    def get(self, request, pk):
        tool = self.get_object(pk)
        serializer = ToolIntegrationSerializer(tool)
        return Response(serializer.data)

    def put(self, request, pk):
        tool = self.get_object(pk)
        serializer = ToolIntegrationSerializer(tool, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tool = self.get_object(pk)
        tool.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ***********************end***************************
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Drug, LowStockAlert, ExpiryAlert, Suplier, PendingOrder
from .serializers import (
    DrugSerializer, LowStockAlertSerializer, ExpiryAlertSerializer,
    SupplierSerializer, PendingOrderSerializer
)


# Drug Views
class DrugListCreateAPIView(APIView):
    def get(self, request):
        drugs = Drug.objects.all().order_by('-id')
        serializer = DrugSerializer(drugs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrugDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Drug, pk=pk)

    def get(self, request, pk):
        drug = self.get_object(pk)
        serializer = DrugSerializer(drug)
        return Response(serializer.data)

    def put(self, request, pk):
        drug = self.get_object(pk)
        serializer = DrugSerializer(drug, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        drug = self.get_object(pk)
        drug.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# LowStockAlert Views
class LowStockAlertListCreateAPIView(APIView):
    def get(self, request):
        alerts = LowStockAlert.objects.all().order_by('-id')
        serializer = LowStockAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LowStockAlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LowStockAlertDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(LowStockAlert, pk=pk)

    def get(self, request, pk):
        alert = self.get_object(pk)
        serializer = LowStockAlertSerializer(alert)
        return Response(serializer.data)

    def put(self, request, pk):
        alert = self.get_object(pk)
        serializer = LowStockAlertSerializer(alert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        alert = self.get_object(pk)
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ExpiryAlert Views
class ExpiryAlertListCreateAPIView(APIView):
    def get(self, request):
        alerts = ExpiryAlert.objects.all().order_by('-id')
        serializer = ExpiryAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpiryAlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpiryAlertDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(ExpiryAlert, pk=pk)

    def get(self, request, pk):
        alert = self.get_object(pk)
        serializer = ExpiryAlertSerializer(alert)
        return Response(serializer.data)

    def put(self, request, pk):
        alert = self.get_object(pk)
        serializer = ExpiryAlertSerializer(alert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        alert = self.get_object(pk)
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Supplier Views
class SupplierListCreateAPIView(APIView):
    def get(self, request):
        suppliers = Supplier.objects.all().order_by('-id')
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Supplier, pk=pk)

    def get(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)

    def put(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        supplier = self.get_object(pk)
        supplier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# PendingOrder Views
class PendingOrderListCreateAPIView(APIView):
    def get(self, request):
        orders = PendingOrder.objects.all().order_by('-id')
        serializer = PendingOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PendingOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingOrderDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(PendingOrder, pk=pk)

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = PendingOrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        serializer = PendingOrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# **************************admin**************************
# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import CustomUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# List & Create users
class UserListCreateAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, Update, Delete a user
class UserDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)