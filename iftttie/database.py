from __future__ import annotations

from contextlib import closing
from datetime import datetime
from pickle import dumps, loads
from sqlite3 import Connection, Row, connect
from typing import List

from loguru import logger

from iftttie.types import Event, Unit


def get_version(db: Connection) -> int:
    with closing(db.cursor()) as cursor:
        return cursor.execute('PRAGMA user_version').fetchone()['user_version']


def init_database(path: str) -> Connection:
    logger.success('Setting up the database…')
    db = connect(path)
    db.row_factory = Row
    migrate(db)
    logger.success('Database is ready.')
    return db


def migrate(db: Connection):
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


def insert_event(db: Connection, event: Event):
    timestamp = event.timestamp.timestamp()
    value = dumps(event.value)
    with db, closing(db.cursor()) as cursor:
        cursor.execute('''
            INSERT OR REPLACE INTO `latest` (`key`, `id`, `value`, `timestamp`, `unit`, `title`)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [event.key, event.id_, value, timestamp, event.unit.value, event.title])
        cursor.execute(
            'INSERT OR REPLACE INTO `log` (`key`, `id`, `value`, `timestamp`) VALUES (?, ?, ?, ?)',
            [event.key, str(event.id_), value, timestamp],
        )


def select_latest(db: Connection) -> List[Event]:
    with closing(db.cursor()) as cursor:
        cursor.execute('''
            SELECT `key`, `id`, `value`, `timestamp`, `unit`, `title` FROM `latest`
            ORDER BY `unit`, `key`
        ''')
        return [make_event(row) for row in cursor.fetchall()]


def make_event(row: Row) -> Event:
    return Event(
        key=row['key'],
        id_=row['id'],
        value=loads(row['value']),
        timestamp=datetime.fromtimestamp(row['timestamp']).astimezone(),
        unit=Unit(row['unit']),
        title=row['title'],
    )


migrations = [
    # Initial schema.
    '''
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

    # I forgot to add the `value` column. And also I need to rename `update_id`.
    # This is early alpha, so just drop and re-create the table.
    '''
        DROP TABLE `log`;
        CREATE TABLE IF NOT EXISTS `log` (
            `key` TEXT NOT NULL,
            `id` TEXT NOT NULL,
            `value` BLOB NOT NULL,
            `timestamp` REAL NOT NULL,
            PRIMARY KEY (`key`, `id`)
        );
        CREATE INDEX IF NOT EXISTS `log_timestamp` ON `log` (`timestamp`);
        PRAGMA user_version = 2;
    ''',

    # For consistency, let's add the `id` column to the `latest` table too.
    '''
        ALTER TABLE `latest` ADD COLUMN `id` TEXT NOT NULL DEFAULT '';
        PRAGMA user_version = 3;
    ''',
]
