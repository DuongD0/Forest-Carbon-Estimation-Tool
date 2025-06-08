import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

class StripeService:
    def create_charge(
        self,
        amount: int, # in cents
        currency: str = "usd",
        source: str = "tok_visa", # This is a test token
        description: str = "Carbon Credit Purchase"
    ) -> stripe.Charge:
        """
        Creates a new charge using the Stripe API.
        In a real application, you would use PaymentIntents for SCA compliance.
        The 'source' would come from a frontend integration with Stripe.js.
        """
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                source=source,
                description=description,
            )
            return charge
        except stripe.error.StripeError as e:
            # Handle Stripe errors (e.g., card declined, invalid request)
            raise ValueError(f"Stripe error: {str(e)}")

stripe_service = StripeService() 