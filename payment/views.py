from django.shortcuts import render, get_object_or_404
import paypalrestsdk
from .models import Course
from django.conf import settings
from django.http import JsonResponse

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET
})


def courses_list(request):
    courses = Course.objects.all()
    
    return render(request, "course_list.html", {"courses":courses})



def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    context = {
        "course": course,
        "CLIENT_ID": settings.PAYPAL_CLIENT_ID
    }
    
    return render(request, "course_detail.html", context)



def create_order(request, course_id):
    """View to handle PayPal order creation"""
    
    course = get_object_or_404(Course, id=course_id)
    
    #Create the PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        
        "payer":{
            "payment_method": "PayPal"
        },
        
        "redirect_urls":{
            "return_url": request.build_absolute_uri(f'/courses/{course_id}/payment-success/'),
            "cancel_url": request.build_absolute_uri('/courses/payment-cancel/')  
        },
        
        "transactions": [{
            "item_list":{
                "items": [{
                    "name": course.name,
                "sku": course.id,
                "price": str(course.price),
                "currency": "USD",
                "quantity": 1
                }]
            },
            
            "amount":{
                "total": str(course.price),
                "currency": "USD"
            },
            
            "description": f"Purcharse of {course.name}"
        }]
    })
    
    if payment.create():
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.rel == "approval_url":
                
                return JsonResponse({'approval_url': link.href})
        
        else:
            return JsonResponse({'error': payment.error}, status=400)



def payment_success(request, course_id):
    """Vie to handle successful PayPal payments"""
    
    course = get_object_or_404(Course, id=course_id)
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    
    context = {
        "payment": payment,
        "course": course
    }
    
    if payment.execute({"payer_id": payer_id}):
        return render(request, 'payment_success.html', context)
    
    
    return JsonResponse({'error': payment.error}, status=400)



def payment_cancel(request):
    """View to handle payment cancellation"""
    return render(request, 'payment_cancel.html')