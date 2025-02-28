import stripe
import json
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Payment history file
os.makedirs("./database", exist_ok=True)
payment_history_path = "./database/payment_history.json"

# Ensure the payment history file exists
if not os.path.exists(payment_history_path):
    with open(payment_history_path, "w") as file:
        json.dump([], file, indent=4)

# Mock users mapped to Stripe test accounts (Replace with real IDs)
users = {
    "Kayla": "acct_test1",
    "Nandan": "acct_test2",
    "Deepak": "acct_test3",
    "Lily": "acct_test4"
}

def process_payment(sender, receiver, amount):
    """Handles the payment process between users."""
    try:
        # Initiate Stripe Transfer
        payment = stripe.Transfer.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            destination=users[receiver],
            description=f"Payment from {sender} to {receiver} via Flexa"
        )

        # Store Payment in JSON History
        payment_data = {
            "transaction_id": payment.id,
            "timestamp": str(datetime.datetime.now()),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "status": "Completed"
        }

        # Update the payment history
        with open(payment_history_path, "r") as file:
            history = json.load(file)
        
        history.append(payment_data)

        with open(payment_history_path, "w") as file:
            json.dump(history, file, indent=4)

        return {"success": True, "message": f"✅ Payment of ${amount} from {sender} to {receiver} was successful!", "payment_id": payment.id}

    except stripe.error.StripeError as e:
        return {"success": False, "message": f"⚠ Payment failed: {str(e)}"}

def get_payment_history():
    """Fetches the stored payment history."""
    if os.path.exists(payment_history_path):
        with open(payment_history_path, "r") as file:
            return json.load(file)
    return []
