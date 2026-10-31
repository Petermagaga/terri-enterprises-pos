from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Grants access only to authenticated owner accounts.
    """

    message = "Only the business owner can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.role == "OWNER"
            and user.is_staff
            and user.is_active
            and user.is_superuser
        )


class IsOwnerOrCashier(BasePermission):
    """
    Grants access to active owner and cashier accounts.
    """

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.is_active
            and user.role in ("OWNER", "CASHIER")
        )