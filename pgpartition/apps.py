import django.apps
from django.conf import settings
import django.db.backends.postgresql.schema as postgresql_schema
from django.db.migrations import state
from django.db.models import options
from django.db.utils import load_backend

from pgpartition import migrations


if "partition" not in options.DEFAULT_NAMES:  # pragma: no branch
    options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + ("partition",)


def patch_migrations():
    """
    Patch the autodetector and model state detection
    """
    if "partition" not in state.DEFAULT_NAMES:  # pragma: no branch
        state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + ("partition",)


def patch_schema_editor():
    """
    Patch the schema editor to allow for partitioned tables and foreign keys
    """
    # if features.schema_editor():  # pragma: no branch
    for config in settings.DATABASES.values():
        backend = load_backend(config["ENGINE"])
        schema_editor_class = backend.DatabaseWrapper.SchemaEditorClass

        if (
            schema_editor_class
            and issubclass(
                schema_editor_class,
                postgresql_schema.DatabaseSchemaEditor,
            )
            and not issubclass(schema_editor_class, migrations.DatabaseSchemaEditorMixin)
        ):
            backend.DatabaseWrapper.SchemaEditorClass = type(
                "DatabaseSchemaEditor",
                (migrations.DatabaseSchemaEditorMixin, schema_editor_class),
                {},
            )


class PGPartitionConfig(django.apps.AppConfig):
    name = "pgpartition"

    def ready(self):
        """
        Do all necessary patching
        """
        patch_migrations()
        patch_schema_editor()
