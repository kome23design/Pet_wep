import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

SUPPORT_EMAIL = "support@royalmaltipoos.shop"
FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", f"Royal Maltipoos <{SUPPORT_EMAIL}>")


def send_branded_email(subject, template_name, context, recipient_list, bcc_admin=False):
    """
    Renders a professional Royal Maltipoos HTML + plain-text email and dispatches it safely.
    """
    try:
        full_context = {
            "BUSINESS_NAME": "Royal Maltipoos",
            "BUSINESS_DOMAIN": "royalmaltipoos.shop",
            "BUSINESS_EMAIL": SUPPORT_EMAIL,
            **(context or {}),
        }
        html_content = render_to_string(template_name, full_context)
        text_content = strip_tags(html_content)

        recipients = [r for r in recipient_list if r]
        if not recipients:
            return False

        bcc = [SUPPORT_EMAIL] if bcc_admin and SUPPORT_EMAIL not in recipients else []

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=FROM_EMAIL,
            to=recipients,
            bcc=bcc,
            reply_to=[SUPPORT_EMAIL],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.warning("Email dispatch warning (%s): %s", subject, exc)
        return False


def send_order_confirmation_email(order):
    """
    Sends a luxury HTML order confirmation email to the customer and notifies support@royalmaltipoos.shop.
    """
    subject = f"Order Confirmation #{order.order_number} — Royal Maltipoos (royalmaltipoos.shop)"
    return send_branded_email(
        subject=subject,
        template_name="emails/order_confirmation_email.html",
        context={"order": order},
        recipient_list=[order.customer_email],
        bcc_admin=True,
    )


def send_order_status_update_email(order, status_notes=""):
    """
    Sends an order status update notification email to the customer.
    """
    subject = f"Order #{order.order_number} Update: {order.get_order_status_display()} — Royal Maltipoos"
    return send_branded_email(
        subject=subject,
        template_name="emails/order_status_update_email.html",
        context={"order": order, "status_notes": status_notes},
        recipient_list=[order.customer_email],
        bcc_admin=False,
    )


def send_contact_inquiry_email(inquiry):
    """
    Sends a confirmation email to the inquirer and notifies support@royalmaltipoos.shop.
    """
    subject = f"We Received Your Inquiry ({inquiry.get_subject_display()}) — Royal Maltipoos"
    return send_branded_email(
        subject=subject,
        template_name="emails/contact_inquiry_email.html",
        context={"inquiry": inquiry},
        recipient_list=[inquiry.email],
        bcc_admin=True,
    )


def send_welcome_account_email(user):
    """
    Sends a welcome email when a user registers an account.
    """
    if not getattr(user, "email", None):
        return False
    subject = "Welcome to Royal Maltipoos — Your Private Client Account"
    return send_branded_email(
        subject=subject,
        template_name="emails/welcome_account_email.html",
        context={"user": user},
        recipient_list=[user.email],
        bcc_admin=False,
    )


def send_password_reset_email(email):
    """
    Sends password reset instructions to the requested email.
    """
    if not email:
        return False
    subject = "Password Reset Instructions — Royal Maltipoos"
    return send_branded_email(
        subject=subject,
        template_name="emails/password_reset_email.html",
        context={"email": email},
        recipient_list=[email],
        bcc_admin=False,
    )


def send_newsletter_welcome_email(email):
    """
    Sends a VIP Private Circle welcome email to newsletter subscribers.
    """
    if not email:
        return False
    subject = "Welcome to the Royal Maltipoos Private VIP Circle"
    return send_branded_email(
        subject=subject,
        template_name="emails/newsletter_welcome_email.html",
        context={"email": email},
        recipient_list=[email],
        bcc_admin=False,
    )
