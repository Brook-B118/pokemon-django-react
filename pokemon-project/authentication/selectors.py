from .models import OIDCIdentity

# Don't know if other Open ID Connect providers use "sub", but this function gets used in google registration route
def get_user_by_oidc_sub(sub, provider):
    # identity = OIDCIdentity.objects.get(sub=userId)
    identity = (
    OIDCIdentity.objects
    .select_related("user")
    .filter(sub=sub, provider=provider)
    .first()
)
    return identity.user if identity else None


