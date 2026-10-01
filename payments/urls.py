from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.payment_page,
        name="payment"
    ),

    path(
        "pay/",
        views.initiate_payment,
        name="initiate_payment"
    ),

    path(
        "callback/",
        views.mpesa_callback,
        name="mpesa_callback"
    ),

]