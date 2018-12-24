from __future__ import annotations

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
        timestamp INTEGER NOT NULL,
        key TEXT NOT NULL,
        value BLOB NOT NULL,
        PRIMARY KEY (key, timestamp)
    );

    -- Latest table contains references to the latest values in the history table.
    CREATE TABLE IF NOT EXISTS latest (
        key TEXT PRIMARY KEY NOT NULL,
        timestamp INTEGER NOT NULL,
        kind TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS latest_kind_key ON latest (kind, key);
'''

SELECT_LATEST_QUERY = '''
    SELECT latest.key AS key, value, latest.timestamp AS timestamp, kind FROM latest
    JOIN history on latest.key = history.key AND latest.timestamp = history.timestamp
    ORDER BY latest.kind, latest.key
'''
SELECT_LATEST_BY_KEY_QUERY = '''
    SELECT latest.key AS key, value, latest.timestamp AS timestamp, kind FROM latest
    JOIN history on latest.key = history.key AND latest.timestamp = history.timestamp
    WHERE latest.key = ?
    ORDER BY latest.kind, latest.key
'''
SELECT_HISTORY_BY_KEY_QUERY = '''
    SELECT timestamp, value FROM history
    WHERE key = ? AND timestamp > ?
    ORDER BY timestamp ASC
'''
