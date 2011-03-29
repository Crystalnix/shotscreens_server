# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from django.contrib import admin

#from gallery.forms import UserRegistrationForm
from registration_app.forms import RecaptchaRegistrationForm

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns = auth_patterns + patterns('',
                                       ('^admin/(.*)', admin.site.root),
                                       (r'^$', 'django.views.generic.simple.direct_to_template',
                                        {'template': 'main.html'}),
#                                       url(r'^account/register/$', 'registration.views.register',
#                                           kwargs={'form_class': UserRegistrationForm},
#                                           name='registration_register'),
                                        url(r'^account/register/$', 'registration.views.register',
                                           kwargs={'form_class': RecaptchaRegistrationForm},
                                           name='registration_register'),
                                       #(r'^accounts/', include('registration_app.urls')),
                                       (r'^downloads/$', 'django.views.generic.simple.direct_to_template',
                                        {'template': 'downloads.html', 'extra_context': {'downloads_active': True}}),
                                       (r'^about/$', 'django.views.generic.simple.direct_to_template',
                                        {'template': 'about.html', 'extra_context': {'about_active': True}}),
                                       ) + urlpatterns
