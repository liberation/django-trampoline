"""
Base test case for trampoline.
"""
from django.test import TransactionTestCase

from trampoline import get_trampoline_config

trampoline_config = get_trampoline_config()


class BaseTestCase(TransactionTestCase):

    def refresh(self):
        trampoline_config.es.indices.refresh('_all')

    def docExists(self, obj):
        doc_type = obj.get_es_doc_type()
        index = obj.get_es_index()
        return trampoline_config.es.exists(
            index=index,
            doc_type=doc_type,
            id=obj.pk
        )

    def aliasExists(self, index, name):
        return trampoline_config.es.indices.exists_alias(
            index=index, name=name)

    def indexExists(self, index):
        return trampoline_config.es.indices.exists(index=index)

    def typeExists(self, index, doc_type):
        return trampoline_config.es.indices.exists_type(
            index=index,
            doc_type=doc_type
        )

    def assertAliasExists(self, index, name):
        self.assertTrue(self.aliasExists(index, name))

    def assertAliasDoesntExist(self, index, name):
        self.assertFalse(self.aliasExists(index, name))

    def assertIndexExists(self, index):
        self.assertTrue(self.indexExists(index))

    def assertIndexDoesntExist(self, index):
        self.assertFalse(self.indexExists(index))

    def assertTypeExists(self, index, doc_type):
        self.assertTrue(self.typeExists(index, doc_type))

    def assertTypeDoesntExist(self, index, doc_type):
        self.assertFalse(self.typeExists(index, doc_type))

    def assertDocExists(self, obj):
        self.assertTrue(self.docExists(obj))

    def assertDocDoesntExist(self, obj):
        self.assertFalse(self.docExists(obj))
