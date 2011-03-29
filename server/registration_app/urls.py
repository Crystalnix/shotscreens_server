from django.conf.urls.defaults import *
from registration.views import register

from registration_app.forms import RecaptchaRegistrationForm

urlpatterns = patterns('',
                       url(r'^register/$', register,
                           {'form_class': RecaptchaRegistrationForm},
                           name='registration.views.register'),
                       (r'', include('registration.urls')),
                       )