import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

class StripeService:
    def create_charge(
        self,
        amount: int, # in cents
        currency: str = "usd",
        source: str = "tok_visa", # test token
        description: str = "Carbon Credit Purchase"
    ) -> stripe.Charge:

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                source=source,
                description=description,
            )
            return charge
        except stripe.error.StripeError as e:
            # handle stripe errors (like card declined)
            raise ValueError(f"Stripe error: {str(e)}")

stripe_service = StripeService() 