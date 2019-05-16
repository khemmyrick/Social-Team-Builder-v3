from django.http.response import HttpResponseRedirect

from projects import views


# Create your views here.
def home(request):
    return HttpResponseRedirect('/v3/projects/search/')
