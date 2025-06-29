import time
import threading
from queue import Queue

chunk_queue = Queue()

def read_file_with_delay(input_file, chunk_size=5, delay_seconds=1):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            while True:
                chunk = ""
                lines_read = 0
                for _ in range(chunk_size):
                    line = infile.readline()
                    if not line:
                        break
                    chunk += line
                    lines_read += 1

                if not chunk:
                    break

                chunk_queue.put(chunk)

                if lines_read == chunk_size:
                    time.sleep(delay_seconds)

        chunk_queue.put(None)

    except:
        chunk_queue.put(None)

def start_reading(input_file, chunk_size=5, delay_seconds=30):
    thread = threading.Thread(target=read_file_with_delay, args=(input_file, chunk_size, delay_seconds))
    thread.daemon = True
    thread.start()

def get_chunk():
    try:
        return chunk_queue.get(timeout=1)
    except:
        return None

if __name__ == "__main__":
    input_filename = "sys_log.txt"
    lines_per_chunk = 5
    delay_between_chunks = 30

    start_reading(input_filename, lines_per_chunk, delay_between_chunks)

    while True:
        chunk = get_chunk()
        if chunk is None:
            break
        print(chunk, end='')
