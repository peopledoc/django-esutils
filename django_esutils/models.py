# -*- coding: utf-8 -*-
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.dispatch import Signal


post_update = Signal(providing_args=['queryset'])


class ESQuerySet(QuerySet):

    def update(self, *args, **kwargs):
        """Udpates and sends post_update signal with current self.
        """
        result = super(ESQuerySet, self).update(*args, **kwargs)
        post_update.send(sender=self.model, queryset=self)
        return result


class ESManager(Manager):

    def get_queryset(self):
        return ESQuerySet(self.model, using=self._db)
