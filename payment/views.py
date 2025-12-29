import json
import base64
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .utils import build_signed_string_from_fields, generate_esewa_signature, generate_transaction_uuid

logger = logging.getLogger(__name__)


class EsewaPaymentAPIView(APIView):
    """
    Endpoint to generate eSewa payment payload with signature
    """

    def post(self, request):
        try:
            # 1. Get amount from request
            amount = request.data.get("amount")
            if not amount:
                return Response({"error": "amount field is required"}, status=400)

            # 2. Fetch merchant credentials
            merchant_code = settings.ESEWA_MERCHANT_CODE
            secret_key = settings.ESEWA_SECRET_KEY
            callback_url = settings.ESEWA_PAYMENT_CALLBACK_URL

            # Log values for debugging
            logger.info(f"ESEWA Merchant Code: {merchant_code}")
            logger.info(f"ESEWA Secret Key: {'SET' if secret_key else 'NOT SET'}")
            logger.info(f"Callback URL: {callback_url}")

            # Validate settings
            if not merchant_code or not secret_key or not callback_url:
                return Response(
                    {"error_message": "Unable to fetch merchant key. Please try again later.", "code": 0},
                    status=500
                )

            # 3. Prepare data for signature
            signed_field_names = ["total_amount", "transaction_uuid", "product_code"]
            transaction_uuid = generate_transaction_uuid()
            total_amount = amount

            data = {
                "total_amount": total_amount,
                "transaction_uuid": transaction_uuid,
                "product_code": merchant_code,
            }

            logger.info(f"Data to sign: {data}")

            # 4. Build signed string
            signed_string = build_signed_string_from_fields(signed_field_names, data)
            logger.info(f"Signed string: {signed_string}")

            # 5. Generate signature
            signature = generate_esewa_signature(secret_key, signed_string)
            logger.info(f"Generated signature: {signature}")

            # 6. Build full payload to send to frontend
            payload = {
                "amount": amount,
                "tax_amount": request.data.get("tax_amount", "0"),
                "total_amount": total_amount,
                "transaction_uuid": transaction_uuid,
                "product_code": merchant_code,
                "product_service_charge": request.data.get("product_service_charge", "0"),
                "product_delivery_charge": request.data.get("product_delivery_charge", "0"),
                "success_url": callback_url,
                "failure_url": callback_url,
                "signed_field_names": ",".join(signed_field_names),
                "signature": signature
            }

            return Response(payload, status=200)

        except Exception as e:
            logger.exception("Error generating eSewa payment payload")
            return Response(
                {"error_message": f"Unable to fetch merchant key. Details: {str(e)}", "code": 0},
                status=500
            )


class EsewaPaymentVerifyView(APIView):
    """
    Endpoint to handle eSewa payment callback and decode the base64 payload
    """

    def get(self, request):
        try:
            data_encoded = request.GET.get("data")
            if not data_encoded:
                return Response({"error": "No data received"}, status=400)

            # Decode base64 payload
            try:
                data_json = base64.b64decode(data_encoded).decode("utf-8")
                data = json.loads(data_json)
            except Exception as e:
                logger.exception("Error decoding eSewa callback data")
                return Response({"error": "Invalid data format"}, status=400)

            return Response({"data": data}, status=200)

        except Exception as e:
            logger.exception("Unexpected error in EsewaPaymentVerifyView")
            return Response({"error": str(e)}, status=500)
