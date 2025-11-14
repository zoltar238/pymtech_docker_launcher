import time

import requests

from .custom_logger import CustomLogger
from ..constants import Constants

logger = CustomLogger()


async def check_service_health(constants: Constants, url: str = None) -> None:
    max_attempts = 20
    attempt = 1
    wait_time = 0.5

    if constants.DOMAIN is not None and not url is None:
        url = f"https://{constants.DOMAIN}"
    else:
        url = f"http://localhost:{constants.ODOO_EXPOSED_PORT}"

    logger.print_status(f"Checking odoo state on: {url}")

    while attempt <= max_attempts:
        try:
            response = requests.head(url, allow_redirects=False)
            status = response.status_code

            if status == 303:
                logger.print_success(f"Odoo is working properly on: {url} (HTTP {status})")
                return
        except requests.RequestException:
            pass

        time.sleep(wait_time)
        attempt += 1

    logger.print_error("Check service logs")
    logger.print_error(f"Service not available on {url} after {max_attempts * wait_time} seconds")
