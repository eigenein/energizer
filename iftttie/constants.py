from __future__ import annotations

from iftttie.enums import ValueKind

LOGURU_FORMAT = ' '.join((
    '<green>{time:MMM DD HH:mm:ss}</green>',
    '<cyan>({name}:{line})</cyan>',
    '<level>[{level:.1}]</level>',
    '<level>{message}</level>',
))
VERBOSITY_LEVELS = {
    0: 'ERROR',
    1: 'WARNING',
    2: 'INFO',
    3: 'DEBUG',
}

DATABASE_INIT_SCRIPT = '''
    -- History table contains all the historical values including the latest ones.
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp FLOAT NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS history_key_timestamp ON history (key, timestamp);
    
    -- Latest table contains references to the latest values in the history table.
    CREATE TABLE IF NOT EXISTS latest (
        history_id INTEGER NOT NULL,
        key TEXT PRIMARY KEY NOT NULL,
        kind TEXT NOT NULL,
        FOREIGN KEY (history_id) REFERENCES history(id)
    );
    CREATE INDEX IF NOT EXISTS latest_kind_key ON latest (kind, key);
'''

VALUE_KIND_TITLES = {
    ValueKind.BEAUFORT: 'Beaufort',
    ValueKind.BOOLEAN: 'Boolean',
    ValueKind.CELSIUS: 'Temperature',
    ValueKind.HPA: 'Pressure',
    ValueKind.HUMIDITY: 'Humidity',
    ValueKind.IMAGE_URL: 'Image',
    ValueKind.MPS: 'Speed',
    ValueKind.OTHER: 'Other',
}
