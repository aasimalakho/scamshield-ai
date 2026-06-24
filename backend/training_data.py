"""
Training data for ScamShield AI's scam classifier.

This is a hand-curated set of example messages covering common scam
types (phishing, romance scams, fake job offers, lottery/prize scams,
tech support scams, fake refunds, impersonation, investment scams) and
everyday legitimate messages. It's intentionally small and readable so
you can extend it easily - just add more (text, label) tuples.

label: 1 = scam, 0 = safe
"""

SCAM_EXAMPLES = [
    # --- Phishing ---
    "Your account has been suspended. Verify your identity now by clicking this link: bit.ly/verify-now or it will be permanently deleted within 24 hours.",
    "URGENT: Unusual sign-in detected on your account. Confirm your password here to secure your account: secure-login-update.com",
    "Your Apple ID has been locked due to suspicious activity. Click here to verify your information immediately.",
    "We detected unauthorized access to your bank account. Please confirm your card number and PIN to restore access.",
    "Your package could not be delivered due to an unpaid customs fee. Pay $2.99 here to release your package: track-delivery-fee.net",
    "Netflix: Your payment was declined. Update your billing information within 12 hours to avoid suspension: netflix-billing-update.com",
    "Security Alert: Someone tried to log into your email from a new device. Click to verify it was you or your account will be locked.",

    # --- Romance scams ---
    "Hello dear, I saw your profile and felt an instant connection. I am a soldier deployed overseas and need help with travel funds to come visit you.",
    "My love, I think about you every day. I need $500 for an emergency medical bill, can you send it through gift cards please my darling.",
    "I have fallen for you so quickly. I want to send you a gift but I need your help paying the customs fee first, my love.",

    # --- Fake job offers ---
    "Congratulations! You've been selected for a work-from-home position paying $5000/week. No experience needed. Send your bank details to start today.",
    "We are hiring immediately, $45/hour, no interview required. Just pay a $50 registration fee to receive your starter kit.",
    "Earn $300 a day doing simple data entry from home. Click here and provide your SSN and banking info to get started right away.",
    "Your resume has been selected! Reply with your full name, date of birth, and bank account to process your first paycheck.",

    # --- Lottery / prize scams ---
    "Congratulations! You've won a $1,000 Walmart gift card. Click here within 24 hours to claim: bit.ly/claim-now",
    "You have been randomly selected to win an iPhone 15! Claim your free prize now before it expires today.",
    "WINNER NOTIFICATION: Your number has been selected in our international lottery. Send your details to claim $250,000 immediately.",
    "You've won a free cruise for two! Just pay a small processing fee of $99 to confirm your booking today.",

    # --- Tech support scams ---
    "Microsoft Support: We detected a virus on your computer. Call this number immediately to remove it and avoid data loss: 1-800-555-0199",
    "Your computer has been infected with a dangerous virus. Do not turn it off. Call our certified technician now to fix it.",
    "Warning! Your device has 5 viruses. Download this tool immediately and call support to clean your system before it's too late.",

    # --- Fake refund / payment ---
    "We have issued a refund of $499 to your account by mistake. Please send it back via gift card immediately or face legal action.",
    "Your JazzCash account has received a refund of Rs 15,000. Click here to confirm and claim the amount within 1 hour.",
    "PayPal: We've refunded you $200 in error. Kindly return the amount using a prepaid card code sent to this number.",

    # --- Impersonation ---
    "This is the IRS. You owe back taxes and a warrant has been issued for your arrest. Call immediately to settle via gift card payment.",
    "This is your bank's fraud department. We need you to confirm your card number and OTP to stop a suspicious transaction.",
    "Hi it's your CEO, I'm in a meeting and need you to urgently buy 3 gift cards and send me the codes, can't talk right now.",
    "This is the police department. Your social security number has been linked to a crime. Pay a fine immediately to avoid arrest.",

    # --- Investment scams ---
    "Turn $100 into $5000 in just one week! Join our exclusive crypto trading group, guaranteed returns, limited spots left.",
    "Our AI trading bot has a 99% win rate. Invest now and double your money in 48 hours, guaranteed, no risk.",
    "Exclusive investment opportunity - guaranteed 40% monthly returns. Send Bitcoin now to secure your spot before it closes.",

    # --- More urgency/pressure based ---
    "ACT NOW: Your subscription expires in 1 hour! Renew immediately by entering your card details or lose access forever.",
    "Final warning: pay the outstanding amount within 30 minutes or legal action will be taken against you immediately.",
    "Your social media account will be deleted in 6 hours unless you verify your identity by sending your password here.",
]

SAFE_EXAMPLES = [
    # --- Everyday personal messages ---
    "Hey, are we still meeting for coffee tomorrow at 10am?",
    "Don't forget to pick up milk on your way home, thanks!",
    "Happy birthday! Hope you have an amazing day, let's catch up soon.",
    "Can you send me the notes from today's class? I missed the last lecture.",
    "Running 10 minutes late, see you at the restaurant soon!",
    "Thanks for helping me move last weekend, I really appreciate it.",
    "What time does the movie start tonight?",
    "Just landed, will call you once I get to the hotel.",

    # --- Legit delivery / order notifications ---
    "Your order #48213 has shipped and is expected to arrive on Thursday. Track it anytime in the app.",
    "Your package was delivered today at 2:15pm. Thanks for shopping with us!",
    "Reminder: your appointment with Dr. Khan is scheduled for tomorrow at 4pm.",
    "Your order has been confirmed. You can view your receipt in your account under order history.",

    # --- Legit work/school messages ---
    "Hi team, the meeting has been moved to 3pm, same Zoom link as before.",
    "Reminder: project submissions are due Friday by 11:59pm.",
    "Thanks for your application, we'd like to schedule a call to discuss your background and the role in more detail.",
    "Your interview is confirmed for Monday at 11am with the engineering team.",
    "Please find attached the agenda for tomorrow's quarterly review meeting.",
    "Your monthly invoice is now available in your account dashboard. No action needed if already paid.",

    # --- Legit banking notifications (no urgency or info requests) ---
    "Your monthly account statement is now available to view online.",
    "A payment of $42.50 was made to Green Grocer using your card ending in 4321.",
    "Your direct deposit of $1,200 has been received and is now available in your account.",
    "This is a reminder that your credit card payment is due on the 28th.",

    # --- Legit promotional (no urgency, no info request) ---
    "Enjoy 10% off your next purchase with code SAVE10, valid through the end of the month, no rush.",
    "New arrivals are here! Check out our spring collection in store and online.",
    "Thanks for being a loyal customer. Here's a coupon for your next visit.",

    # --- Legit social / community ---
    "The community potluck is this Saturday at 5pm, bring a dish if you can!",
    "Our book club is meeting Thursday evening to discuss chapter 6, see you there.",
    "Reminder that the gym will be closed this Sunday for maintenance.",
    "Looking forward to seeing everyone at the reunion next month!",

    # --- Legit family ---
    "Mom says dinner is at 7, don't be late.",
    "Can you grab grandma from the airport at 6pm on Saturday?",
    "Sent you the photos from the trip, let me know what you think!",
]


def get_training_data():
    """Return (texts, labels) for training the classifier."""
    texts = SCAM_EXAMPLES + SAFE_EXAMPLES
    labels = [1] * len(SCAM_EXAMPLES) + [0] * len(SAFE_EXAMPLES)
    return texts, labels
