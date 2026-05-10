from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("Accès refusé")

        return wrapper
    return decorator