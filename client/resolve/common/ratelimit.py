from time import time, sleep
from threading import Lock
from urllib.parse import urlparse


class RateLimiter:
    """Per domain token bucket rate limiter"""
    
    def __init__(self, requests_per_second: float = 2.0):
        self._rate = requests_per_second
        self._buckets: dict[str, float] = {}
        self._lock = Lock()
    
    def acquire(self, url: str) -> None:
        """Block until request can proceed"""
        domain = urlparse(url).netloc
        
        with self._lock:
            now = time()
            
            if domain not in self._buckets:
                self._buckets[domain] = now
                return
            
            last_request = self._buckets[domain]
            min_interval = 1.0 / self._rate
            time_since_last = now - last_request
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                sleep(sleep_time)
                self._buckets[domain] = time()
            else:
                self._buckets[domain] = now
