import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from .models import Payment
from .mpesa import stk_push


def payment_page(request):
    return render(request, "payments/payment.html")


def initiate_payment(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    phone = request.POST.get("phone")
    amount = request.POST.get("amount")

    if not phone or not amount:
        return JsonResponse(
            {"error": "Phone and amount are required"},
            status=400
        )

    if phone.startswith("0"):
        phone = "254" + phone[1:]

    if phone.startswith("+"):
        phone = phone[1:]

    payment = Payment.objects.create(
        phone=phone,
        amount=amount,
        status="PENDING"
    )

    callback_url = (
        "https://YOUR-PUBLIC-DOMAIN.com/mpesa/callback/"
    )

    try:

        response = stk_push(
            phone=phone,
            amount=amount,
            callback_url=callback_url
        )

        payment.checkout_request_id = response.get(
            "CheckoutRequestID"
        )

        payment.merchant_request_id = response.get(
            "MerchantRequestID"
        )

        payment.result_code = response.get(
            "ResponseCode"
        )

        payment.result_description = response.get(
            "ResponseDescription"
        )

        payment.save()

        return JsonResponse(response)

    except Exception as e:

        payment.status = "FAILED"
        payment.result_description = str(e)
        payment.save()

        return JsonResponse(
            {"error": str(e)},
            status=500
        )


def mpesa_callback(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    data = json.loads(request.body)

    callback = data["Body"]["stkCallback"]

    checkout_request_id = callback.get(
        "CheckoutRequestID"
    )

    result_code = callback.get(
        "ResultCode"
    )

    result_description = callback.get(
        "ResultDesc"
    )

    try:

        payment = Payment.objects.get(
            checkout_request_id=checkout_request_id
        )

    except Payment.DoesNotExist:

        return JsonResponse(
            {"error": "Payment not found"},
            status=404
        )

    payment.result_code = str(result_code)
    payment.result_description = result_description

    if result_code == 0:

        payment.status = "SUCCESS"

        metadata = callback.get(
            "CallbackMetadata",
            {}
        )

        items = metadata.get(
            "Item",
            []
        )

        for item in items:

            if item.get("Name") == "MpesaReceiptNumber":

                payment.mpesa_receipt = item.get(
                    "Value"
                )

    else:

        payment.status = "FAILED"

    payment.save()

    return JsonResponse(
        {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }
    )