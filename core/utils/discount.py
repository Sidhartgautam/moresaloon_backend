from decimal import Decimal
from offers.models import SaloonOffers, SaloonCoupons
from django.core.exceptions import ValidationError

def calculate_discounted_price(total_price, saloon_id, applied_offer_id=None, coupon_code=None):
    """
    Calculate the discounted price based on the applied offer or coupon.
    """
    if applied_offer_id and coupon_code:
        raise ValidationError("Only one of 'offer' or 'coupon' can be applied at a time.")

    discounted_price = total_price

    # Apply Offer
    if applied_offer_id:
        try:
            offer = SaloonOffers.objects.get(id=applied_offer_id, saloon_id=saloon_id)
            if not offer.is_active():
                raise ValidationError("The selected offer is not active.")
            if offer.percentage_discount:
                discounted_price = total_price * (1 - Decimal(offer.percentage_discount) / 100)
            elif offer.fixed_discount:
                discounted_price = max(0, total_price - offer.fixed_discount)
        except SaloonOffers.DoesNotExist:
            raise ValidationError("Invalid offer.")

    # Apply Coupon
    if coupon_code:
        try:
            coupon = SaloonCoupons.objects.get(code=coupon_code, saloon_id=saloon_id)
            if not coupon.is_active():
                raise ValidationError("The provided coupon code is not active.")
            if coupon.percentage_discount:
                discounted_price = total_price * (1 - Decimal(coupon.percentage_discount) / 100)
            elif coupon.fixed_discount:
                discounted_price = max(0, total_price - coupon.fixed_discount)
        except SaloonCoupons.DoesNotExist:
            raise ValidationError("Invalid coupon code.")

    return discounted_price