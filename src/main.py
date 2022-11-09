import random
import threading
import time
import redis
import logging
import os
import datetime
import psycopg2
import uuid

logger = logging.Logger(__name__)

FILE_QUEUE = 'file_queue'

conn = redis.Redis(host='redis', port=6379, db=0)


def init_redis():
    pool = redis.ConnectionPool(host='redis', port=6379, db=0)
    conn = redis.Redis(connection_pool=pool)
    conn.ping()
    return pool


def load_images(pool):
    logger.warning('load_images start...')
    conn = redis.Redis(connection_pool=pool)

    files = os.listdir('photo')
    for file in files:
        logger.warning(f"LOADING: load file: {file}")
        with open(os.path.join('photo', file), 'rb') as file_b:
            data = file_b.read()
            conn.rpush(FILE_QUEUE, data)


def save_images(pool):
    logger.warning('save_images start...')
    conn = redis.Redis(connection_pool=pool)
    db_conn = psycopg2.connect(dbname='backend_db', user='backend_user',
                               password='backend_password', host='postgres_db')

    while True:
        file = conn.lpop(FILE_QUEUE)
        if file is None:
            time.sleep(1)
        else:
            save(file, db_conn)
            logger.warning(f'SAVING: Th:{threading.get_native_id()} saved')


def save(file, conn):
    with conn.cursor() as cursor:
        file_size = len(file)
        created_at = datetime.datetime.now()
        cursor.execute(f"INSERT INTO files(created_at, file_size) VALUES ('{created_at}', {file_size})")
        logger.warning(f"DB: INSERT: {file_size}, {created_at}")


def init_photos():
    logger.warning('Init photos started...')
    if not os.path.exists('photo'):
        os.makedirs('photo')

    for i in range(1000):
        file_name = str(uuid.uuid4()) + '.png'
        file_size = random.randint(200, 1400)
        with open(os.path.join('photo', file_name), 'wb+') as file:
            file.write(os.urandom(file_size))
    logger.warning('Init photos successful!')


if __name__ == '__main__':
    init_photos()
    time.sleep(5)  # wait for postgres to start
    pool = init_redis()
    thr1 = threading.Thread(target=load_images, args=(pool, )).start()
    thr2 = threading.Thread(target=save_images, args=(pool, )).start()
    thr3 = threading.Thread(target=save_images, args=(pool, )).start()
