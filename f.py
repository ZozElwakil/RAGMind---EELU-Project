
import os, re, logging
logger = logging.getLogger(__name__)

db_url = os.getenv("DATABASE_URL", "")
safe = re.sub(r":([^:@/]+)@", ":***@", db_url)
logger.info(f"Runtime DATABASE_URL = {safe}")
