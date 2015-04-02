# -*- coding: utf-8 -*-
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.dispatch import Signal


post_update = Signal(providing_args=['queryset'])


class ESQuerySet(QuerySet):

    def update(self, *args, **kwargs):
        """Udpates and sends post_update signal with current self.
        """
        # keep ids to update
        ids = list(self.values_list('pk', flat=True))

        # do update
        result = super(ESQuerySet, self).update(*args, **kwargs)

        # call signal with queryset matching the update
        new_qs = self.model.objects.filter(pk__in=ids)
        # trigger signal
        post_update.send(sender=self.model, queryset=new_qs)

        return result


class ESManager(Manager):

    def get_queryset(self):
        return ESQuerySet(self.model, using=self._db)
