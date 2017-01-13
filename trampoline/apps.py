"""
App config for trampoline.
"""
from copy import deepcopy
import collections

import logging
import six

from elasticsearch import Elasticsearch

from django.conf import settings
from django.db import transaction
from django.db.models.signals import class_prepared
from django.db.models.signals import post_delete
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


DEFAULT_TRAMPOLINE = {
    'HOSTS': [
        {'host': 'localhost'},
    ],
    'MODELS': [],
    'OPTIONS': {
        'fail_silently': True,
        'disabled': False,
        'celery_queue': None
    },
}


def recursive_update(d, u):
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def post_save_es_index(sender, instance, **kwargs):
    if instance.is_indexable():
        try:
            # post_save fires after the save occurs but before the transaction
            # is commited.
            transaction.on_commit(lambda: instance.es_index())
        except AttributeError:
            # 1s countdown waiting for the transaction to complete.
            instance.es_index(countdown=1)


def post_delete_es_delete(sender, instance, **kwargs):
    instance.es_delete()


def class_prepared_check_indexable(sender, **kwargs):
    trampoline_config = get_trampoline_config()

    # Only register indexation signals for models defined in the settings.
    sender_path = '{0}.{1}'.format(sender.__module__, sender.__name__)
    if sender_path not in trampoline_config.models_paths:
        return

    post_save.connect(
        post_save_es_index,
        sender=sender,
        weak=False,
        dispatch_uid='trampoline_post_save_{0}'.format(sender.__name__)
    )
    post_delete.connect(
        post_delete_es_delete,
        sender=sender,
        weak=False,
        dispatch_uid='trampoline_post_delete_{0}'.format(sender.__name__)
    )


class TrampolineConfig(AppConfig):
    name = 'trampoline'
    verbose_name = "Trampoline"

    def __init__(self, *args, **kwargs):
        class_prepared.connect(class_prepared_check_indexable)
        super(TrampolineConfig, self).__init__(*args, **kwargs)

    def ready(self):
        self._es = Elasticsearch(hosts=self.hosts)

    @property
    def settings(self):
        USER_TRAMPOLINE = getattr(settings, 'TRAMPOLINE', {})
        TRAMPOLINE = deepcopy(DEFAULT_TRAMPOLINE)
        return recursive_update(TRAMPOLINE, USER_TRAMPOLINE)

    @property
    def es(self):
        return self._es

    @property
    def indexable_models(self):
        models = []
        for model_path in self.models_paths:
            module_path, model_name = model_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[''])
            model = getattr(module, model_name)
            if model not in models:
                models.append(model)
        return models

    @property
    def hosts(self):
        return self.settings['HOSTS']

    @property
    def models_paths(self):
        return self.settings['MODELS']

    @property
    def should_fail_silently(self):
        return self.settings['OPTIONS']['fail_silently']

    @property
    def is_disabled(self):
        return self.settings['OPTIONS']['disabled']

    @property
    def celery_queue(self):
        return self.settings['OPTIONS']['celery_queue']

try:
    # Try to import AppConfig to check if this feature is available.
    from django.apps import AppConfig  # noqa
except ImportError:
    app_config = TrampolineConfig()
    app_config.ready()

    def get_trampoline_config():
        return app_config
else:
    def get_trampoline_config():
        from django.apps import apps
        return apps.get_app_config('trampoline')
