from django.http.response import HttpResponseRedirect


# Create your views here.
def home(request):
    return HttpResponseRedirect('/v3/projects/search/')
