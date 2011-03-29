# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('gallery.views',
    (r'^$', 'gallery'),
    (r'^create_admin_user$', 'create_admin_user'),
    (r'^create_album/$', 'create_album'),
    (r'^upload_picture/$', 'upload_picture'),
    (r'^download/(?P<key>.+)/(?P<name>.+)$', 'download_file'),
    (r'^review/(?P<key>.+)/(?P<name>.+)$', 'review_picture'),
    (r'^cover/(?P<key>.+)/(?P<name>.+)$', 'download_cover'),
    (r'^small/(?P<key>.+)/(?P<name>.+)$', 'download_small'),
    (r'^album/(?P<key>.+)$', "show_album"),
    (r'^delete/(?P<key>.+)$', "delete_picture"),
    (r'^delete_ok/(?P<key>.+)$', "delete_picture_ok"),
    (r'^delete_album/(?P<key>.+)$', "delete_album"),
    (r'^delete_album_ok/(?P<key>.+)$', "delete_album_ok"),
    (r'^list_album/$', 'list_album'),
    (r'^user_info/$', 'user_info'),
    (r'^upload/$', 'upload_file'),
    (r'^tasks/clear_old_picture/$', 'clear_old_picture'),
)