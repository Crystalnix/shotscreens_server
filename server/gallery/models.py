# -*- coding: utf-8 -*-
import sys
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from django.contrib.auth.models import User
from django.db.models import permalink

class Album(db.Model):
    name = db.StringProperty()
    owner = db.ReferenceProperty(User)
    created_date = db.DateTimeProperty(auto_now_add=True)

    @permalink
    def get_absolute_url(self):
        """ Функция для объекта, возвращает прямую ссылку на альбом """
        return ('gallery.views.show_album', (), {'key': self.key()})

    @permalink
    def get_cover_url(self):
        """
            Функция для объекта, возвращает прямую ссылку на обложку альбома.
            P.S обложкой служит первое изображение из альбома, если альбом пустой,
                то функция отдает False, и на клиенте выводится изображение по дефолту (указано в шаблоне)
        """
        cover = Picture.all().filter("album =", self.key())
        res = cover.fetch(1)
        if not len(res)==0:
            return ('gallery.views.download_cover', (), {'key': res[0].key(), 'name': res[0].name})
        else:
            return False

    class Meta:
        ordering = ['name']


class Picture(db.Model):
    submitter = db.ReferenceProperty(User)
    submitted_date = db.DateTimeProperty(auto_now_add=True)
#    title = db.StringProperty()
    caption = db.StringProperty(multiline=True)
    album = db.ReferenceProperty(Album, required=True)
    data = db.BlobProperty(required=True)
    data_cover = db.BlobProperty()
    data_small = db.BlobProperty()
    name = db.StringProperty(required=True)

    @permalink
    def get_absolute_url(self):
        """ Функция для объекта, возвращает прямую ссылку на картинку из БД """
        return ('gallery.views.download_file', (), {'key': self.key(),
                                                    'name': self.name+".png"})
    @permalink
    def get_cover_url(self):
        """ Функция для объекта, возвращает прямую ссылку на картинку из БД """
        return ('gallery.views.download_cover', (), {'key': self.key(),
                                                    'name': self.name+".png"})
    @permalink
    def get_small_url(self):
        """ Функция для объекта, возвращает прямую ссылку на картинку из БД """
        return ('gallery.views.download_small', (), {'key': self.key(),
                                                    'name': self.name+".png"})

    @permalink
    def get_view_url(self, key, name):
        return ('gallery.views.view_picture', (), {'key': key,
                                                    'name': name+".png"})

    def __unicode__(self):
        return u'File: %s' % self.name


#----------
class Filetest(db.Model):
    """ Тестовая модель для upload image"""
    data = db.BlobProperty(required=True)
    name = db.StringProperty()
#----------

class Settings(db.Model):
    days_for_old_picture = db.IntegerProperty()
    width_for_cover_album = db.IntegerProperty()
    width_for_small_picture = db.IntegerProperty()