from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from time import sleep
from client.resolve.common.ratelimit import RateLimiter


class HTTPClient:
    """Simple HTTP client with rate limiting"""
    
    def __init__(self):
        self._limiter = RateLimiter()
        self._user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        max_retries: int = 3
    ) -> str:
        """GET request with retries"""
        
        self._limiter.acquire(url)
        
        req_headers = {
            "User-Agent": self._user_agent,
            "Accept": "*/*",
        }
        
        if headers:
            req_headers.update(headers)
        
        request = Request(url, headers=req_headers)
        
        for attempt in range(max_retries):
            try:
                with urlopen(request, timeout=10) as response:
                    return response.read().decode('utf-8')
            except HTTPError as e:
                if e.code == 429:  # Rate limited
                    backoff = 2 ** attempt
                    sleep(backoff)
                    continue
                elif attempt == max_retries - 1:
                    raise
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                sleep(1)
        
        return ""
