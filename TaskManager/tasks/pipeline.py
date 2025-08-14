from social_core.exceptions import AuthAlreadyAssociated
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth

User = get_user_model()

def associate_by_email_or_get_existing_user(backend, uid, details, user=None, *args, **kwargs):
    email = details.get('email')
    if user:
        return {'user': user}  # Already authenticated

    if not email:
        return

    # Check if the UID is already linked to someone
    existing_social = UserSocialAuth.objects.filter(provider=backend.name, uid=uid).first()
    if existing_social:
        return {'user': existing_social.user}  # ✅ Login the existing user

    # Try to find a Django user with this email
    try:
        existing_user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    # Associate this social login with the existing user
    UserSocialAuth.objects.create(user=existing_user, provider=backend.name, uid=uid)
    return {'user': existing_user}



from social_core.exceptions import AuthForbidden

# BLOCKED_EMAILS = ['admin@example.com']  # Add other restricted emails here if needed

# def auth_allowed(backend, details, response=None, *args, **kwargs):
#     email = details.get('email')
#     if email in BLOCKED_EMAILS:
#         raise AuthForbidden(backend)  # ✅ Blocks login via Google for that email


def set_user_as_normal_user(backend, user=None, *args, **kwargs):
    if user and (user.is_staff or user.is_superuser):
        user.is_staff = False
        user.is_superuser = False
        user.save()


from social_core.exceptions import AuthForbidden

BLOCKED_EMAILS = ['admin@example.com', 'superuser@example.com']

def auth_allowed(backend, details, response=None, *args, **kwargs):
    email = details.get('email')
    if email in BLOCKED_EMAILS:
        raise AuthForbidden(backend)  # 🚫 Block Google login
