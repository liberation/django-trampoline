"""
Management command for trampoline.
"""
from __future__ import print_function
from multiprocessing import Pool
from optparse import make_option
import itertools
import logging
import sys

from tqdm import tqdm

from elasticsearch_dsl import Index

from django.contrib.contenttypes.models import ContentType
from django.db import connection

from trampoline.management.base import ESBaseCommand
from trampoline.tasks import es_index_object
from trampoline.tasks import STATUS_FAILED
from trampoline.tasks import STATUS_IGNORED
from trampoline.tasks import STATUS_INDEXED


logger = logging.getLogger(__name__)


def index_object(object_id, content_type_id, target_name, dry_run):
    connection.close()
    result = {
        'status': STATUS_INDEXED,
        'object_id': object_id,
        'content_type_id': content_type_id,
    }
    if not dry_run:
        try:
            result['status'] = es_index_object.run(
                target_name,
                content_type_id,
                object_id,
                fail_silently=False
            )
        except Exception as exc:
            result['status'] = STATUS_FAILED
            result['exc'] = exc
    return result


def star_index_object(args):
    return index_object(*args)


class Command(ESBaseCommand):
    help = (
        "Create documents on {0}{1}INDEX_NAME{2} based on the method "
        "{0}get_indexable_queryset{2} on the related models."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index_name'],
        ESBaseCommand.options['target_name'],
    )
    required_options = ('index_name',)

    def run(self, *args, **options):
        self.target_name = self.target_name or self.index_name
        self.log_file = open('trampoline.log', 'w')

        index = Index(self.target_name)
        if not index.exists():
            self.print_error(
                u"Index '{0}' does not exist."
                .format(self.target_name)
            )
            sys.exit(1)

        self.print_info(u"Indexing objects on '{0}'.".format(self.target_name))

        models = self.trampoline_config.get_index_models(self.index_name)

        for model in models:
            queryset = model.get_indexable_queryset()
            object_ids = queryset.values_list('pk', flat=True).iterator()
            object_count = queryset.count()
            content_type_id = ContentType.objects.get_for_model(model).pk

            model_name = model.__name__
            self.print_info(u"Processing model: '{0}'.".format(model_name))

            self.progress_status = {
                STATUS_INDEXED: 0,
                STATUS_FAILED: 0,
                STATUS_IGNORED: 0,
            }
            desc = self.get_progress_bar_desc(self.progress_status)
            self.progress_bar = tqdm(
                total=object_count,
                dynamic_ncols=True,
                desc=desc
            )

            pool = Pool(None, maxtasksperchild=100)
            imap_results = pool.imap_unordered(
                star_index_object,
                itertools.izip(
                    object_ids,
                    itertools.repeat(content_type_id),
                    itertools.repeat(self.target_name),
                    itertools.repeat(self.dry_run)
                )
            )
            try:
                for result in imap_results:
                    self.indexation_callback(result)
            except KeyboardInterrupt:
                pool.terminate()
                pool.join()
            else:
                pool.close()
                pool.join()

            self.progress_bar.close()

        self.log_file.close()
        self.print_success("Indexation completed.")

    def indexation_callback(self, result):
        status = result['status']
        if status in self.progress_status:
            self.progress_status[status] += 1

        exc = result.get('exc')
        if exc is not None:
            print(
                "FAILED: pk {0} (content_type {1})"
                .format(
                    result['content_type_id'],
                    result['object_id'],
                ),
                str(exc),
                file=self.log_file
            )

        desc = self.get_progress_bar_desc(self.progress_status)
        self.progress_bar.set_description(desc)
        self.progress_bar.update()

    def get_progress_bar_desc(self, progress_status):
        desc = (
            "{0}S {1} {2}F {3} {4}I {5}{6}"
            .format(
                self.GREEN,
                progress_status[STATUS_INDEXED],
                self.RED,
                progress_status[STATUS_FAILED],
                self.YELLOW,
                progress_status[STATUS_IGNORED],
                self.RESET,
            )
        )
        return desc
