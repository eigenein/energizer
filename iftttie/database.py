from __future__ import annotations

from datetime import datetime
from pickle import loads, dumps
from sqlite3 import Row
from typing import List

import aiosqlite

from iftttie.dataclasses_ import Update
from iftttie.enums import Unit

INIT_SCRIPT = '''
    CREATE TABLE IF NOT EXISTS `latest` (
        `key` TEXT PRIMARY KEY NOT NULL,
        `value` BLOB NOT NULL,
        `timestamp` REAL NOT NULL,
        `unit` TEXT NOT NULL,
        `title` TEXT NULL
    );
'''

# noinspection SqlResolve
SELECT_LATEST_QUERY = '''
    SELECT `key`, `value`, `timestamp`, `unit`, `title` FROM latest
    ORDER BY `unit`, `key`
'''


async def init_database(db: aiosqlite.Connection):
    db.row_factory = aiosqlite.Row
    await db.executescript(INIT_SCRIPT)


async def insert_update(db: aiosqlite.Connection, update: Update):
    timestamp = update.timestamp.timestamp()
    await db.execute(
        'INSERT OR REPLACE INTO `latest` (`key`, `value`, `timestamp`, `unit`, `title`) VALUES (?, ?, ?, ?, ?)',
        (update.key, dumps(update.value), timestamp, update.unit.value, update.title),
    )
    await db.commit()


async def select_latest(db: aiosqlite.Connection) -> List[Update]:
    async with db.execute(SELECT_LATEST_QUERY) as cursor:  # type: aiosqlite.Cursor
        return [update_from_row(row) for row in await cursor.fetchall()]


def update_from_row(row: Row) -> Update:
    return Update(
        key=row['key'],
        value=loads(row['value']),
        timestamp=datetime.fromtimestamp(row['timestamp']).astimezone(),
        unit=Unit(row['unit']),
        title=row['title'],
    )
