from functools import wraps
from django.shortcuts import redirect
def login_required_auth0():
    def requires_auth(f):
      @wraps(f)
      def decorated(request, *args, **kwargs):
        if not autheticate_auth0(request):
          # Redirect to Login page here
          return redirect('/auth/login/')
        return f(request, *args, **kwargs)
      return decorated
    return requires_auth

def autheticate_auth0(request):
    if 'profile' in request.session:
        return True
    return False
