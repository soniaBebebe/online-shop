from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
from .pdf import generate_order_pdf

def send_order_confirmation(order):
    subject=f"your order #{order.id} is confirmed"
    message=render_to_string("shop/email/order_confirmation.txt",{
        "order":order
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )

def send_order_receipt(order):
    subject=f"receipt for your order #{order.id}"
    message=render_to_string("shop/email/order_receipt.txt",{
        "order":order
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )

def notify_admin(order):
    subject=f"rnew order received #{order.id}"
    message=render_to_string("shop/email/order_notify_admin.txt",{
        "order":order
    })

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ["sonctonc@gmail.com"],
        fail_silently=False,
    )

def send_order_pdf(order):
    pdf_buffer=generate_order_pdf(order)

    email=EmailMessage(
        subject=f"Your receipt for order #{order.id}",
        body="Please find attached your PDF receipt.",
        from_email="shop@example.com",
        to=[order.email]
    )
    email.attach(f"receipt_{order.id}.pdf", pdf_buffer.read(), "application/pdf")
    email.send()