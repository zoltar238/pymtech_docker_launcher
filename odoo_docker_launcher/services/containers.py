import os
import subprocess
from typing import Any

from odoo_docker_launcher.constants import Constants
from odoo_docker_launcher.services.custom_logger import CustomLogger

logger = CustomLogger()


def stop_running_containers(constants: Constants) -> None:
    """
    Stops all running containers of this deployment
    param config: contains all the relevant configurations and objects needed for deployment
    return: None
    """
    logger.print_header("STOPPING RUNNING CONTAINERS")

    try:
        # Shut down running containers
        logger.print_status("Stopping running containers")
        subprocess.run(
            "docker compose down",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            cwd=constants.BASE_DIR
        )

        logger.print_success("Running containers were successfully stopped")
    except subprocess.CalledProcessError as e:
        logger.print_error(f"Error stopping running containers: {str(e)}")
        logger.print_critical(f"Aborting deployment: {e.stderr}")
        exit(1)


def build_docker_images(constants: Constants) -> None:
    logger.print_header("APPLYING CONFIGURATION CHANGES")
    try:
        logger.print_status("Building container images")
        subprocess.run(
            f"docker compose build",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=constants.BASE_DIR
        )
        logger.print_success("Container images were successfully built")
    except subprocess.CalledProcessError as e:
        logger.print_error(f"Error building docker images: {str(e)} \n {e.stderr} \n {e.stdout}")
        exit(1)


def launch_database_only(constants: Constants) -> None:
    logger.print_status("Launching database")
    try:
        subprocess.run(
            f"docker compose up -d db",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=constants.BASE_DIR
        )
    except subprocess.CalledProcessError as e:
        logger.print_error(f"Error starting up database: {str(e)} \n {e.stderr} \n {e.stdout}")
        exit(1)


def get_database_names(constants: Constants) -> list[Any] | None:
    for i in range(10):
        try:
            # Verify that the container is running properly before attempting to get the database names
            while True:
                cmd_check = f"docker exec {constants.COMPOSE_PROJECT_NAME}_db pg_isready -U odoo"
                result = subprocess.run(
                    cmd_check,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=constants.BASE_DIR,
                )

                if "accepting connections" in result.stdout:
                    logger.print_success("PostgreSQL is ready!")
                    break

            cmd_list_databases = f"docker exec {constants.COMPOSE_PROJECT_NAME}_db psql -U odoo -l -A"
            result = subprocess.run(
                cmd_list_databases,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=constants.BASE_DIR,
            )

            # Get all databases that aren't part of postgres
            lines = result.stdout.split('\n')
            databases = []

            for index, line in enumerate(lines):
                if '|' in line:
                    db_name = line.split('|')[0].strip()
                    if db_name not in ['template_postgis', 'postgres', 'template0', 'template1',
                                       'Name'] and '=' not in db_name:
                        databases.append(db_name)

            return databases
        except subprocess.CalledProcessError as e:
            if i > 9:
                logger.print_warning(
                    f"Failed getting databases names on try {i + 1}: \n{str(e)} \n{e.stderr} \n{e.stdout}")
    return None


def launch_containers(constants: Constants, command: str = None) -> None:
    """
    Deploys the docker containers
    :return: None
    """
    try:

        # Base command
        base_cmd = f"docker compose -f docker-compose.yml"
        if command:
            subprocess.run(
                f"{base_cmd} run --rm odoo {command}",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=constants.BASE_DIR
            )
        else:
            logger.print_status("Spinning up containers")
            subprocess.run(
                f"{base_cmd} up -d",
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=constants.BASE_DIR
            )
            logger.print_success("Containers were successfully started")

    except subprocess.CalledProcessError as e:
        logger.print_error(f"Error launching containers: {str(e)}")
        logger.print_critical(f"Aborting deployment: {e.stderr}")
        show_logs_on_error(constants)
        exit(1)


def show_logs_on_error(constants: Constants) -> None:
    logger.print_header("FAILURE LOGS")

    # Show docker logs
    logger.print_status("Displaying Docker container logs:")
    try:
        cmd = f"docker compose -f docker-compose.yml logs --tail=30"
        output = subprocess.check_output(cmd, shell=True).decode()
        logger.print_warning(output)
    except subprocess.CalledProcessError as e:
        logger.print_error(f"Error getting Docker logs: {str(e)}")

    print()

    # Odoo logs
    odoo_logs_path = f"{constants.BASE_DIR}/log/odoo-server.log"
    if os.path.exists(odoo_logs_path):
        logger.print_status("Displaying Odoo server logs:")
        with open(odoo_logs_path, "r", encoding="UTF-8") as f:
            lines = f.readlines()[-50:]
            logger.print_warning("".join(lines))
    else:
        logger.print_warning(f"Odoo log file not found at path: {odoo_logs_path}")
