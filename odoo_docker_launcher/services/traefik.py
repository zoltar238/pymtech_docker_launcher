import configparser
import os.path

from .custom_logger import CustomLogger

logger = CustomLogger()


def update_proxy_mode(odoo_container_path: str, target: str) -> None:
    try:
        logger.print_status("Verifying odoo proxy config")

        config_file = os.path.join(odoo_container_path, "config", "odoo.conf")

        # Verify if the file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Read the existing configuration file
        config_override = configparser.ConfigParser()
        config_override.read(config_file)

        # Ensure the 'options' section exists
        if 'options' not in config_override:
            config_override.add_section('options')

        # Update the proxy_mode option
        if target == "prod":
            config_override.set('options', 'proxy_mode', 'True')
        else:
            config_override.set('options', 'proxy_mode', 'False')

        # Write back to the file
        with open(config_file, 'w') as configfile:
            config_override.write(configfile)

        logger.print_success("Odoo proxy config has been updated")
    except Exception as e:
        logger.print_error(f"Failed to update odoo proxy config: {e}")
