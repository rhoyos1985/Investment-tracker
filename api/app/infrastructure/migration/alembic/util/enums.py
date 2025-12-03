from enum import Enum

class MigrationAction(str, Enum):
    ERROR = "error"
    UPDATED = "updated"
    NOTUPDATED = "no_updated"
    PENDING = "pending"
    NOTPENDING = "not_pending"
    MIGRATIONAPPLIED = "migration_applied"
    NOTMIGRATIONAPPLIED = "no_migration_applied"
