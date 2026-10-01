import base64
import requests

from datetime import datetime
from django.conf import settings


def get_access_token():

    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate"

    response = requests.get(
        url,
        params={
            "grant_type": "client_credentials"
        },
        auth=(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        )
    )

    response.raise_for_status()

    return response.json()["access_token"]


def get_password(timestamp):

    data = (
        settings.MPESA_SHORTCODE
        + settings.MPESA_PASSKEY
        + timestamp
    )

    return base64.b64encode(
        data.encode()
    ).decode()


def stk_push(phone, amount, callback_url):

    access_token = get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = get_password(timestamp)

    url = (
        f"{settings.MPESA_BASE_URL}"
        "/mpesa/stkpush/v1/processrequest"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": "DjangoPayment",
        "TransactionDesc": "Django M-Pesa Payment",
    }

    response = requests.post(
        url,
        json=data,
        headers=headers
    )

    response.raise_for_status()

    return response.json()