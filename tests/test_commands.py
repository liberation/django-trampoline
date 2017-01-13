"""
Test management commands for trampoline.
"""
from django.conf import settings
from django.core.management import call_command

from tests.base import BaseTestCase
from tests.models import Token


class TestCommands(BaseTestCase):

    def tearDown(self):
        super(TestCommands, self).tearDown()
        # Delete remnants of previous tests.
        self.deleteIndex('foobar_target')
        self.deleteIndex('foobar')
        self.deleteIndex(Token.get_es_index())

    def test_es_create_documents(self):
        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token)

        # Dry run.
        call_command('es_create_documents', dry_run=True)
        self.assertDocDoesntExist(token)

        call_command('es_create_documents')
        self.assertDocExists(token)

        settings.TRAMPOLINE['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.TRAMPOLINE['OPTIONS']['disabled'] = False

        call_command('es_create_documents')
        self.assertDocDoesntExist(token)

    def test_es_create_indices(self):
        # Dry run.
        call_command('es_create_indices', dry_run=True)
        self.assertIndexDoesntExist(Token.get_es_index())

        call_command('es_create_indices')
        self.assertIndexExists(Token.get_es_index())

        # Skip already created indices silently.
        call_command('es_create_indices')

    def test_es_create_alias(self):
        # Index name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                target='foobar_target'
            )

        # Target name required.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index='foobar'
            )

        # Index doesn't exist.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index='foobar',
                target='foobar_target'
            )

        self.createIndex('foobar_target')

        # Alias with same name as index.
        with self.assertRaises(SystemExit):
            call_command(
                'es_create_alias',
                index='foobar_target',
                target='foobar_target'
            )

        # Dry run.
        call_command(
            'es_create_alias',
            index='foobar',
            target='foobar_target',
            dry_run=True
        )
        self.assertAliasDoesntExist(index='foobar_target', name='foobar')

        call_command(
            'es_create_alias',
            index='foobar',
            target='foobar_target'
        )
        self.assertAliasExists(index='foobar_target', name='foobar')
