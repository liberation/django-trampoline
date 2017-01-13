![logo_trampoline](https://cloud.githubusercontent.com/assets/1875772/17204131/fb27a2dc-54a3-11e6-80b2-e6e46d84bdfe.png)

[![Build Status](https://travis-ci.org/laurentguilbert/django-trampoline.svg?branch=develop)](https://travis-ci.org/laurentguilbert/django-trampoline)
[![Coverage Status](https://coveralls.io/repos/github/laurentguilbert/django-trampoline/badge.svg?branch=develop)](https://coveralls.io/github/laurentguilbert/django-trampoline?branch=develop)
[![PyPI](https://img.shields.io/pypi/v/django-trampoline.svg)](https://pypi.python.org/pypi/django-trampoline)

Trampoline provides you with tools to easily setup, manage and index your Django models in ElasticSearch. It uses **celery** and is heavily reliant on **elasticsearch_dsl**.

It was designed to allow re-indexing of your documents without any downtime by using intermediary indices along with aliases.

## Installation

To install the package simply run:

```
pip install django-trampoline
```

## Settings

Add `trampoline` to your `INSTALLED_APPS`.

Define the setting:
```python
TRAMPOLINE = {
    'HOSTS': [
        {'host': 'localhost'},
    ],
    'MODELS': [],
    'OPTIONS': {
        'celery_queue': None,
        'fail_silently': True,
        'disabled': False,
    },
}
```

### HOSTS

`localhost` is already set by default.

Mapping of the different ElasticSearch hosts used in your project.

### MODELS

### OPTIONS

#### celery_queue

`None` by default.

Specify which Celery queue should handle your indexation tasks.

#### fail_silently

`True` by default.

If `fail_silently` is `True` exceptions raised while indexing are caught and logged without being re-raised.

#### disabled

`False` by default.

## ESIndexableMixin

```python
from trampoline.mixins import ESIndexableMixin
```

In order to make your model indexable you must make it inherit from `ESIndexableMixin` and implement a few things.

#### es_serializer (required)

#### get_es_doc_type_mapping (optional)

#### is_indexable (optional)

```python
def is_indexable(self):
    return True
```

Tell whether a particular instance of the model should be indexed or skipped (defaults to true).

#### get_indexable_queryset (optional)

```python
@classmethod
def get_indexable_queryset(cls):
    return []
```

Return the list of contents that should be indexed for this model using the command `es_create_documents()` defined bellow. Make sure you don't forget the `classmethod` decorator.

## Management commands

All management commands accept the following arguments:
- **--help**: Display an help message and the available arguments for the command.
- **--dry-run**: Run the command in dry run mode without actually changing anything.
- **--verbosity**: 0 to 3 from least verbose to the most. Default to 1.

### es_create_indices

### es_create_alias

### es_create_documents
