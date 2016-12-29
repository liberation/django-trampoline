"""
Celery tasks for trampoline.
"""
import logging

from django.contrib.contenttypes.models import ContentType

from celery import shared_task

from trampoline import get_trampoline_config


logger = logging.getLogger(__name__)
trampoline_config = get_trampoline_config()

STATUS_INDEXED = 0
STATUS_FAILED = 1
STATUS_IGNORED = 2
STATUS_DELETED = 3


@shared_task
def es_index_object(
        index,
        content_type_id,
        object_id,
        fail_silently=None):
    """
    Index objects based on the methods defined by EsIndexableMixin.
    """
    if fail_silently is None:
        fail_silently = trampoline_config.should_fail_silently
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.model_class()._default_manager.get(pk=object_id)
        if not obj.is_indexable():
            return STATUS_IGNORED

        doc_type = obj.get_es_doc_type()
        body = obj.get_es_body()
        trampoline_config.es.create(
            index=index,
            doc_type=doc_type,
            id=obj.pk,
            body=body
        )
    except:
        if fail_silently:
            logger.error(
                "Exception occured while indexing object.",
                exc_info=True,
                extra={
                    'index': index,
                    'content_type_id': content_type_id,
                    'object_id': object_id,
                }
            )
            return STATUS_FAILED
        else:
            raise
    return STATUS_INDEXED


@shared_task
def es_delete_doc(
        index,
        doc_type,
        doc_id,
        fail_silently=None):
    """
    Delete a document from the index.
    """
    if fail_silently is None:
        fail_silently = trampoline_config.should_fail_silently
    try:
        trampoline_config.es.delete(
            index=index,
            doc_type=doc_type,
            id=doc_id,
            ignore=404,
        )
    except:
        if trampoline_config.should_fail_silently:
            logger.error(
                "Exception occured while deleting document.",
                exc_info=True,
                extra={
                    'index_name': index,
                    'doc_type': doc_type,
                    'doc_id': doc_id,
                }
            )
            return STATUS_FAILED
        else:
            raise
    return STATUS_DELETED
