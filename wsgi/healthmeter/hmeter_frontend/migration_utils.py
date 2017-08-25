# Taken from git://github.com/ASKBOT/django-south-app-rename-example.git
"""utils to help rename apps and South migrations."""
import os
from south.models import MigrationHistory


def was_applied(migration_file_path, app_name):
    """true if migration with a given file name ``migration_file``
    was applied to app with name ``app_name``"""
    try:
        migration_file = os.path.basename(migration_file_path)
        migration_name = migration_file.split('.')[0]
        MigrationHistory.objects.get(app_name=app_name,
                                     migration=migration_name)
        return True
    except MigrationHistory.DoesNotExist:
        return False
