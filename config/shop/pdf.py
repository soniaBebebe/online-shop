from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.http import HttpResponse
from datetime import datetime

def generate_order_pdf(order):
    from io import BytesIO
    buffer=BytesIO()

    p=canvas.Canvas(buffer,pagesize=A4)
    width, height = A4

    y=height-30*mm
    p.setFont("Times-Bold", 18)
    p.drawString(20*mm,y, "My Online Shop -- Receipt")
    y -=15*mm

    p.setFont("Times-Roman", 12)
    p.drawString(20*mm,y,f"Order #: {order.id}")
    y -=7*mm
    p.drawString(20*mm,y, f"Date: {order.created.strftime('%Y-%m-%d %H:%M')}")
    y -=10*mm

    p.line (20*mm, y, 190*mm, y)
    y -=10*mm

    p.setFont("Times-Bold", 12)
    p.drawString(20*mm, y, "Product")
    p.drawString(120*mm, y, "Qty")
    p.drawString(150*mm, y, "Price")
    y -=8*mm

    p.setFont("Times-Roman",11)

    for item in order.items.all():
        p.drawString(20*mm, y, item.product.name)
        p.drawString(120*mm, y, str(item.quantity))
        p.drawString(150*mm, y, f"{item.get_cost()}$")
        y -=6*mm
    y -=10*mm
    p.line(20*mm, y, 190*mm, y)
    y -=10*mm

    p.setFont("Times-Bold", 14)
    p.drawString(20*mm, y, f"Total: {order.get_total_cost()}$")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer