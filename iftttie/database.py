from __future__ import annotations

from contextlib import closing
from datetime import datetime
from pickle import dumps, loads
from sqlite3 import Connection, Row, connect
from typing import List

from loguru import logger

from iftttie.types import Unit, Update


def get_version(db: Connection) -> int:
    with closing(db.cursor()) as cursor:
        return cursor.execute('PRAGMA user_version').fetchone()['user_version']


def init_database(path: str) -> Connection:
    logger.success('Setting up the database…')
    db = connect(path)
    db.row_factory = Row

    version = get_version(db)
    logger.info('Database version: {}.', version)

    logger.info('Running migrations…')
    for i, script in enumerate(migrations, start=1):
        if i > version:
            logger.info('Applying migration #{}…', i)
            with db:
                db.executescript(script)
            logger.success('Applied migration #{}.', i)
        else:
            logger.debug('Migration #{} is already applied.', i)

    logger.success('Database is ready.')
    return db


def insert_update(db: Connection, update: Update):
    timestamp = update.timestamp.timestamp()
    with db, closing(db.cursor()) as cursor:
        cursor.execute(
            'INSERT OR REPLACE INTO `latest` (`key`, `value`, `timestamp`, `unit`, `title`) VALUES (?, ?, ?, ?, ?)',
            [update.key, dumps(update.value), timestamp, update.unit.value, update.title],
        )
        cursor.execute(
            'INSERT OR REPLACE INTO `log` (`key`, `update_id`, `timestamp`) VALUES (?, ?, ?)',
            [update.key, str(update.id_), timestamp],
        )


def select_latest(db: Connection) -> List[Update]:
    with closing(db.cursor()) as cursor:
        cursor.execute('''
            SELECT `key`, `value`, `timestamp`, `unit`, `title` FROM `latest`
            ORDER BY `unit`, `key`
        ''')
        return [update_from_row(row) for row in cursor.fetchall()]


def update_from_row(row: Row) -> Update:
    return Update(
        key=row['key'],
        value=loads(row['value']),
        timestamp=datetime.fromtimestamp(row['timestamp']).astimezone(),
        unit=Unit(row['unit']),
        title=row['title'],
    )


migrations = [
    '''
        -- Initial schema.

        CREATE TABLE IF NOT EXISTS `latest` (
            `key` TEXT PRIMARY KEY NOT NULL,
            `value` BLOB NOT NULL,
            `timestamp` REAL NOT NULL,
            `unit` TEXT NOT NULL,
            `title` TEXT NULL
        );

        CREATE TABLE IF NOT EXISTS `log` (
            `key` TEXT NOT NULL,
            `update_id` TEXT NOT NULL,
            `timestamp` REAL NOT NULL,
            PRIMARY KEY (`key`, `update_id`)
        );
        CREATE INDEX IF NOT EXISTS `log_timestamp` ON `log` (`timestamp`);

        PRAGMA user_version = 1;
    ''',
]
