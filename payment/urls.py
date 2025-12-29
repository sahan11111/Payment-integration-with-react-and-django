from django.urls import path
from .views import EsewaPaymentAPIView, EsewaPaymentVerifyView

urlpatterns = [
    # Endpoint to generate the eSewa payment payload (with signature)
    path("payments/esewa/", EsewaPaymentAPIView.as_view(), name="esewa-payment"),

    # Callback URLs after payment
    path("payments/esewa/verify/", EsewaPaymentVerifyView.as_view(), name="esewa-success"),
]