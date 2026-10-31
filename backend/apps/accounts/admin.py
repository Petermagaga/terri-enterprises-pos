
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Grants access only to active business owners.
    """

    message = "Only the business owner can access this resource."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and user.is_active
            and user.role == "OWNER"
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


"""
then about invoices creation and exposed to pdf (my idea was cash can highlight different product put into something like cart and in that there is total and an option of creating that list as invoice with supermarket logo
"""