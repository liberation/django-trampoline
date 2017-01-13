"""
Management command for trampoline.
"""
from trampoline.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Delete the alias from {0}{1}INDEX{2} to {0}{1}TARGET{2}."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index'],
        ESBaseCommand.options['target']
    )
    required_options = ('index', 'target')

    def run(self, *args, **options):
        self.confirm(
            u"Are you really sure you want to delete the alias '{0}' ?"
            .format(self.index)
        )
        if not self.dry_run:
            self.trampoline_config.es.indices.delete_alias(
                index=self.target,
                name=self.index
            )
        self.print_success(
            u"Deleted alias '{0}' from '{1}'.".format(self.target, self.index)
        )
