import urllib.robotparser
import urllib.request
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_allowed_by_robots(url: str, user_agent: str) -> bool:
    try:
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            return True
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        
        req = urllib.request.Request(
            robots_url,
            headers={'User-Agent': user_agent}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            rp.parse(response.read().decode('utf-8').splitlines())
            
        allowed = rp.can_fetch(user_agent, url)
        logger.info(f"Robots check for {url}: allowed={allowed}")
        return allowed
    except Exception as e:
        logger.warning(f"Failed to fetch/parse robots.txt for {url}: {e}. Defaulting to True.")
        return True
