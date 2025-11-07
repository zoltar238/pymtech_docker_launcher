import os
from dataclasses import fields

import typer

from odoo_docker_launcher.constants import get_constants
from odoo_docker_launcher.services.custom_logger import CustomLogger

logger = CustomLogger()
cwd = os.getcwd()

constants = get_constants(cwd)

app = typer.Typer(
    help="Env file operations",
    no_args_is_help=True,
)


@app.command()
def validate():
    # Determine environment mode
    mode = "Production" if constants.DEPLOYMENT_TARGET == "prod" else "Development"
    logger.print_header("VERIFYING ENVIRONMENT VARIABLES")
    logger.print_status("--- Core Configuration ---")
    logger.print_status(f"Project name: {constants.COMPOSE_PROJECT_NAME}")
    logger.print_status(f"Deployment target:{mode}")
    logger.print_status("--- Container Versions ---")
    logger.print_status(f"Odoo version: {constants.ODOO_VERSION}")
    logger.print_status(f"Postgres version: {constants.POSTGRES_VERSION}")
    logger.print_status("--- Network & Connectivity ")
    logger.print_status(f"Odoo exposed port: {constants.ODOO_EXPOSED_PORT}")
    logger.print_status(f"Odoo internal port: {constants.ODOO_INTERNAL_PORT}")
    logger.print_status(f"Domain: {constants.DOMAIN}")
    logger.print_status("--- Files & Paths ---")
    logger.print_status(f"Odoo log path: {constants.ODOO_LOG}")
    logger.print_status(f"Odoo config path: {constants.ODOO_CONFIG}")
    logger.print_status(f"Odoo addons path: {constants.ADDONS_FOLDER}")
    logger.print_status("--- Module Management ---")
    logger.print_status(f"Auto install modules: {constants.AUTO_INSTALL_MODULES}")
    logger.print_status(f"Auto update modules: {constants.AUTO_UPDATE_MODULES}")
    logger.print_status(f"Force update modules: {constants.FORCE_UPDATE}")
    logger.print_status(f"Update module list: {constants.UPDATE_MODULE_LIST}")
    logger.print_status("--- Build & Development ---")
    logger.print_status(f"Rebuild images: {constants.FORCE_REBUILD}")
    logger.print_status("--- Optional Features ---")
    logger.print_status(f"Install wisper for voice recognition: {constants.OPTIONAL_WHISPER}")

    # Variables can't be null
    nullable_vars = {'DOMAIN', 'UPDATE_MODULE_LIST'}

    for field in fields(constants):
        value = getattr(constants, field.name)
        if field.name not in nullable_vars and (value is None or value == ''):
            logger.print_error(f"Variable {field.name} can't be null")
            exit(1)

    try:
        # Odoo version must be correct
        if constants.ODOO_VERSION not in ['16', '17', '18', '19', 'latest']:
            logger.print_error(
                f"La versión de Odoo: {constants.ODOO_VERSION} no es válida. Debe ser 16, 17 o 18")
            exit(1)
        # Deployment target must be correct
        if constants.DEPLOYMENT_TARGET not in ['dev', 'prod']:
            logger.print_error(f"Target inválido. Debe ser 'dev' o 'prod'")
            exit(1)
        # Check it the addons path exists
        if not os.path.exists(constants.ADDONS_FOLDER):
            logger.print_error(f"The addons path: {constants.ADDONS_FOLDER} does not exist")
            exit(1)

        logger.print_success("Environment variables verified successfully")

    except ValueError:
        logger.print_error(f"Port {constants.ODOO_EXPOSED_PORT} must be a number")


if __name__ == "__main__":
    app()
