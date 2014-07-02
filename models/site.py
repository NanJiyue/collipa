# coding: utf-8

from pony.orm import Optional, LongUnicode
from ._base import db, SessionMixin, ModelMixin
import config

config = config.rec()


class Site(db.Entity, SessionMixin, ModelMixin):
    name = Optional(unicode)

    help = Optional(LongUnicode)
    about = Optional(LongUnicode)
    contact = Optional(LongUnicode)
    service = Optional(LongUnicode)
    pravicy = Optional(LongUnicode)
    law = Optional(LongUnicode)
    description = Optional(LongUnicode)

    ico_img = Optional(unicode, 400)
    head_img = Optional(unicode, 400)
    background_img = Optional(unicode, 400)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Site: %s>' % self.id
