import logging
import threading
import time
from file_watcher import start_watching


def main():
    path = r"C:\test\uploads"
    t = threading.Thread(target=start_watching, args=(path,))
    t.start()

    while True:
        logging.info('Main thread is still running...')
        time.sleep(120)


if __name__ == '__main__':
    main()
