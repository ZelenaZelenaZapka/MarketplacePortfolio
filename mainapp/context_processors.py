def user_role(request):
    is_seller = False
    is_customer = False
    seller = None
    customer = None

    if request.user.is_authenticated:
        if hasattr(request.user, "seller"):
            is_seller = True
            seller = request.user.seller

        if hasattr(request.user, "customer"):
            is_customer = True
            customer = request.user.customer

    return {
        "is_seller": is_seller,
        "is_customer": is_customer,
        "seller_profile": seller,
        "customer_profile": customer,
    }