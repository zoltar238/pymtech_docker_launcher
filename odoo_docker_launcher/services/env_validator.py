import os
from dataclasses import fields

from .constants import Constants


def env_verify(constants: Constants) -> None:
    # Determine environment mode
    mode = "Production" if constants.DEPLOYMENT_TARGET == "prod" else "Development"
    constants.logger.print_header("VERIFYING ENVIRONMENT VARIABLES")
    constants.logger.print_status("--- Core Configuration ---")
    constants.logger.print_status(f"Project name: {constants.COMPOSE_PROJECT_NAME}")
    constants.logger.print_status(f"Deployment target:{mode}")
    constants.logger.print_status("--- Container Versions ---")
    constants.logger.print_status(f"Odoo version: {constants.ODOO_VERSION}")
    constants.logger.print_status(f"Postgres version: {constants.POSTGRES_VERSION}")
    constants.logger.print_status("--- Network & Connectivity ")
    constants.logger.print_status(f"Odoo exposed port: {constants.ODOO_EXPOSED_PORT}")
    constants.logger.print_status(f"Odoo internal port: {constants.ODOO_INTERNAL_PORT}")
    constants.logger.print_status(f"Domain: {constants.DOMAIN}")
    constants.logger.print_status("--- Files & Paths ---")
    constants.logger.print_status(f"Odoo log path: {constants.ODOO_LOG}")
    constants.logger.print_status(f"Odoo config path: {constants.ODOO_CONFIG}")
    constants.logger.print_status(f"Odoo addons path: {constants.ADDONS_FOLDER}")
    constants.logger.print_status("--- Module Management ---")
    constants.logger.print_status(f"Auto install modules: {constants.AUTO_INSTALL_MODULES}")
    constants.logger.print_status(f"Auto update modules: {constants.AUTO_UPDATE_MODULES}")
    constants.logger.print_status(f"Force update modules: {constants.FORCE_UPDATE}")
    constants.logger.print_status(f"Update module list: {constants.UPDATE_MODULE_LIST}")
    constants.logger.print_status("--- Build & Development ---")
    constants.logger.print_status(f"Rebuild images: {constants.FORCE_REBUILD}")
    constants.logger.print_status("--- Optional Features ---")
    constants.logger.print_status(f"Install wisper for voice recognition: {constants.OPTIONAL_WHISPER}")

    # Variables can't be null
    nullable_vars = {'DOMAIN', 'UPDATE_MODULE_LIST'}

    for field in fields(constants):
        value = getattr(constants, field.name)
        if field.name not in nullable_vars and (value is None or value == ''):
            constants.logger.print_error(f"Variable {field.name} can't be null")
            exit(1)

    try:
        # Odoo version must be correct
        if constants.ODOO_VERSION not in ['16', '17', '18', 'latest']:
            constants.logger.print_error(
                f"La versión de Odoo: {constants.ODOO_VERSION} no es válida. Debe ser 16, 17 o 18")
            exit(1)
        # Deployment target must be correct
        if constants.DEPLOYMENT_TARGET not in ['dev', 'prod']:
            constants.logger.print_error(f"Target inválido. Debe ser 'dev' o 'prod'")
            exit(1)
        # Check it the addons path exists
        if not os.path.exists(constants.ADDONS_FOLDER):
            constants.logger.print_error(f"The addons path: {constants.ADDONS_FOLDER} does not exist")
            exit(1)

        constants.logger.print_success("Environment variables verified successfully")

    except ValueError:
        constants.logger.print_error(f"Port {constants.ODOO_EXPOSED_PORT} must be a number")
