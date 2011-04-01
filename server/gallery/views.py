# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext as _
from ragendja.template import render_to_response as _render_to_response

from mimetypes import guess_type

from gallery.models import Album, Picture, Settings
from gallery.forms import AlbumForm, PictureForm, FiletestForm

from django.views.generic.list_detail import object_list
from django.views.generic.create_update import create_object, delete_object
from django.core.urlresolvers import reverse
from google.appengine.ext import db
#from google.appengine.ext.db import stats
from django.contrib.auth.models import User
from google.appengine.api import images, memcache

from django.shortcuts import render_to_response

import datetime
from django.utils import simplejson as json
from django.conf import settings

from django.core.paginator import Paginator, InvalidPage, EmptyPage



def gallery(request):
    """ Выводит список альбомом. """
    if request.user.is_authenticated():
        return object_list(request, Album.all().filter("owner =", request.user))
    else:
        return HttpResponseRedirect('/account/login/')

def show_album(request, key):
    """ Выводит изображения альбома. Выборку делаем по ключу. """
    if request.user.is_authenticated():
        pic_list = Picture.all().filter("album", db.Key(key))
        paginator = Paginator(pic_list, 10)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            pic = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pic = paginator.page(paginator.num_pages)
        return render_to_response('picture_list.html', {"pics": pic, "user":request.user})
    else:
        return HttpResponseRedirect('/account/login/')

def picture_carousel(request, key):
    if request.user.is_authenticated():
        return object_list(request, Picture.all().filter("album", db.Key(key)), template_name='picture_carousel.html')
    else:
        return HttpResponseRedirect('/account/login/')

def list_album(request):
    """
        Для desktop клиента отдаем список имен всех альбомов пользователя
    """
    if request.user.is_authenticated():
        return object_list(request, Album.all().filter("owner =", request.user), template_name="list_name.html")
    else:
        return HttpResponseRedirect('/account/login/')

def create_album(request):
    if request.user.is_authenticated():
        class AddAlbumForm(AlbumForm):
            """
                Для того что бы получить в классе формы
                к объекту request.user переопределяем класс AlbumForm во views
            """
            def save(self):
                album = super(AddAlbumForm, self).save(commit=False)
                album.owner = request.user # при сохранение, поле заполняем данными из request
                album.save()
                return album
        return create_object(request, form_class=AddAlbumForm,
                             post_save_redirect=reverse('gallery.views.upload_picture'))
    else:
        return HttpResponseRedirect('/account/login/')

def upload_picture(request):
    if request.user.is_authenticated():
        if request.user.free_size < 0:
            raise Http404('Not free space...')
        class AddPictureForm(PictureForm):
            """
                Для того что бы получить в классе формы
                к объекту request.user переопределяем класс PictureForm во views
            """
            def __init__(self, *args, **kwargs):
                super(PictureForm, self).__init__(*args, **kwargs)
                self.fields['album'].queryset = Album.all().filter("owner =", request.user) # переопределяем запрос так что бы выбор был только между альбомами владельцем которых является текущий пользователь (request.user)
#                query = Album.all().filter("owner =", request.user).fetch(999)
                album_list_name = []
#                for data in query:
#                    album_list_name.append((str(data.key()), data.name))
#                self.fields['album'].choices = album_list_name
                self.fields['album'].choices = [(x.key(), x.name) for x in Album.all().filter("owner =", request.user)] # генератор списка кортежей для списка альбомов
            def save(self):
                picture = super(AddPictureForm, self).save(commit=False)
                picture.submitter = request.user # при сохранение, поле заполняем данными из request

                picture.data = images.rotate(picture.data, 0)

                try:
                    width_samll = Settings.all().get().width_for_small_picture
                    width_cover = Settings.all().get().width_for_cover_album
                except:
                    width_samll = getattr(settings, 'WIDTH_FOR_SMALL_PICTURE', 400)
                    width_cover = getattr(settings, 'WIDTH_FOR_COVER_ALBUM', 200)
                picture.data_small = images.resize( picture.data, width=width_samll)
                picture.data_cover = images.resize( picture.data, width=width_cover)

                # код для контролирования кол-ва занимаемого места
                user_free_size = User.get(request.user.key())
                user_free_size.free_size = user_free_size.free_size - len(picture.data) - len(picture.data_small) - len(picture.data_cover)
                user_free_size.put()

                picture.save()
                return picture
        return create_object(request, form_class=AddPictureForm,
                             post_save_redirect=reverse('gallery.views.gallery'))
    else:
        return HttpResponseRedirect('/account/login/')


def download_file(request, key, name):
    """ Отдаем картинку из БД по ключу и имени файла получаемые из запроса по url'у"""

    file = memcache.get("full_"+key)
    if file is not None:
        return HttpResponse(file,
                            content_type='image/png',
                            mimetype='image/png')
    else:
        file = Picture.get(db.Key(key))
        memcache.add("full_"+key, file.data)
        if file.name != name:
            raise Http404('Could not find file with this name!') # если имя файла не соответсвует существующему то выводим сообщение
        return HttpResponse(file.data,
                            content_type='image/png',
                            mimetype='image/png')

#    file = Picture.get(db.Key(key)) # db.KEY преобразует ключ из текстовой формы в объект KYE
#    if file.name != name:
#        raise Http404('Could not find file with this name!') # если имя файла не соответсвует существующему то выводим сообщение
#    return HttpResponse(file.data,
#                            content_type=guess_type(file.name)[0] or 'application/octet-stream')

def download_cover(request, key, name):
    """ Отдаем картинку из БД по ключу и имени файла получаемые из запроса по url'у"""
    file = memcache.get("cover_" + key)
    if file is not None:
        return HttpResponse(file,
                            content_type='image/png',
                            mimetype='image/png')
    else:
        file = Picture.get(db.Key(key))
        memcache.add("cover_" + key, file.data_cover)
        if file.name != name:
            raise Http404('Could not find file with this name!')
        return HttpResponse(file.data_cover,
                            content_type='image/png',
                            mimetype='image/png')

def download_small(request, key, name):
    """ Отдаем картинку из БД по ключу и имени файла получаемые из запроса по url'у"""
    file = memcache.get("small_" + key)
    if file is not None:
        return HttpResponse(file,
                            content_type='image/png',
                            mimetype='image/png')
    else:
        file = Picture.get(db.Key(key))
        memcache.add("small_" + key, file.data)
        if file.name != name:
            raise Http404('Could not find file with this name!')
        return HttpResponse(file.data_small,
                            content_type='image/png',
                            mimetype='image/png')

def delete_picture(request, key):
    """ Удаление изображения по ключу передаваемого из url'а """
    if request.user.is_authenticated():
        pic = Picture.get(db.Key(key))
        size = len(pic.data)+len(pic.data_cover)+len(pic.data_small)
        return delete_object(request, Picture, object_id=db.Key(key),
            post_delete_redirect=reverse('gallery.views.delete_picture_ok', args=[size]))
    else:
        return HttpResponseRedirect('/account/login/')

def delete_picture_ok(request, key):
    """ при успешном удаление картинки, освобождаем свободное место пользователя """
    if request.user.is_authenticated():
        # код для контролирования кол-ва занимаемого места
        user_free_size = User.get(request.user.key())
        user_free_size.free_size = user_free_size.free_size + int(key)
        user_free_size.put()
        return HttpResponseRedirect('/gallery')
    else:
        return HttpResponseRedirect('/account/login/')

def delete_album(request, key):
    """ Удаление альбома по ключу передаваемого из url'а """
    if request.user.is_authenticated():
        return delete_object(request, Album, object_id=db.Key(key),
            post_delete_redirect=reverse('gallery.views.delete_album_ok', args=[key]))
    else:
        return HttpResponseRedirect('/account/login/')

def delete_album_ok(request, key):
    """ при успешном удаление альбома, освобождаем свободное место пользователя """
    if request.user.is_authenticated():
        pictures = Picture.all().filter('album', db.Key(key)).fetch(999)
        size = 0
        for pic in pictures:
            size = size + len(pic.data) + len(pic.data_cover) + len(pic.data_small)
            pic.delete()
        # код для контролирования кол-ва занимаемого места
        user_free_size = User.get(request.user.key())
        user_free_size.free_size = user_free_size.free_size + size
        user_free_size.put()
        return HttpResponseRedirect('/gallery')
    else:
        return HttpResponseRedirect('/account/login/')

#----------
def upload_file(request):
    """ Тестовая страница upload image"""
    return create_object(request, form_class=FiletestForm,
                             post_save_redirect=reverse('gallery.views.gallery'))
#----------

def create_admin_user(request):
    """
        Создать администратора для админки джанги
            username: admin
            password: f558e93e820166e1d497ebe5d6a15f9f
            email: adm.shotscreens@gmail.com
        Пароль md5 хэш от adm.shotscreens@gmail.com
    """
    user = User.get_by_key_name('adm.shotscreens@gmail.com')
    if not user or user.username != 'adm.shotscreens@gmail.com' or not (user.is_active and
            user.is_staff and user.is_superuser and
            user.check_password('admin')):
        user = User(key_name='adm.shotscreens@gmail.com', username='adm.shotscreens@gmail.com',
            email='adm.shotscreens@gmail.com', first_name='adm.shotscreens@gmail.com', last_name='adm.shotscreens@gmail.com',
            is_active=True, is_staff=True, is_superuser=True)
        user.set_password('f558e93e820166e1d497ebe5d6a15f9f')
        user.put()
    return _render_to_response(request, 'gallery/admin_created.html')

def review_picture(request, key, name):
    picture = Picture.get(db.Key(key))
    query_list_image = Picture.all().filter("album", picture.album).fetch(999)
    try:
        next = query_list_image[query_list_image.index(picture)+1]
    except:
        next = False
    try:
        if not query_list_image.index(picture)==0:
            last = query_list_image[query_list_image.index(picture)-1]
        else:
            last = False
    except:
        last = False
    return render_to_response('view_picture.html', {'picture':picture, 'next':next, 'last':last, 'user': request.user})

def clear_old_picture(request):
    """
        Функция для выполнения в cron
        Удаляет изображения старше * дней (значение берется из настроек в БД)
    """
    try:
        days = Settings.all().get().days_for_old_picture
    except:
        days = getattr(settings, 'DAYS_FOR_OLD_PICTURE', 30)
    query = Picture.all().filter("submitted_date <", datetime.datetime.today() - datetime.timedelta(days=days))
    response = HttpResponse()
    for pic in query:
        response.write("<br/>Delete: "+str(pic.name))

        # код для контролирования кол-ва занимаемого места
        user_free_size = User.get(pic.submitter.key())
        user_free_size.free_size = user_free_size.free_size + len(pic.data) + len(pic.data_small) + len(pic.data_cover)
        user_free_size.put()

        pic.delete()
    response.write("<br/>Delete END: "+str(len(query)))
    return response

def user_info(request):
    if request.user.is_authenticated():
        user = User.get(request.user.key())
        user_info = {}
        user_info['free_size'] = user.free_size
        user_info['username'] = user.username
        user_info['last_login'] = user.last_login.strftime("%A, %d. %B %Y %I:%M%p")
        user_info['date_joined'] = user.date_joined.strftime("%A, %d. %B %Y %I:%M%p")
        response = HttpResponse(mimetype='text/javascript')
        response.write(json.dumps(user_info))
        return response
    else:
        return HttpResponseRedirect('/account/login/')