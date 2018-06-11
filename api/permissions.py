from rest_framework import permissions

from api.utils import is_solver, is_instructor


class IsOwnerOrSolverOrInstructor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):  # pragma: no cover
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if is_instructor(request.user):
            return True
        elif request.method == 'GET' and view.action == 'retrieve':
            return obj.user == request.user or\
                   is_solver(obj.problem, request.user)

        return True


class IsOwnerOrInstructor(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):  # pragma: no cover
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if is_instructor(request.user):
            return True
        elif request.method == 'GET' and view.action == 'retrieve':
            return obj.submission.user == request.user

        return True
