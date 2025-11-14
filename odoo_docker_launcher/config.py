import configparser
import os

import psutil
import typer

from odoo_docker_launcher.services.custom_logger import CustomLogger

app = typer.Typer(
    no_args_is_help=True,
    add_completion=True,
    help="Configuration files operations"
)

base_dir = os.getcwd()

logger = CustomLogger()


@app.command(help="Automatically configure Odoo and Postgres for efficient resource usage")
def auto_config() -> None:
    logger.print_header("Setting up Odoo configuration")

    cpu_count = os.cpu_count()
    system_ram = psutil.virtual_memory().total

    # Total ram available for Odoo
    odoo_ram = system_ram * 0.65
    # Total ram available for Postgres
    postgres_ram = system_ram * 0.2

    # Odoo config parameters
    workers = cpu_count * 2
    max_cron_threads = 1
    limit_memory_soft = int(odoo_ram / (cpu_count + max_cron_threads))
    limit_memory_hard = int(limit_memory_soft * 1.40)
    db_maxconn = 32

    # Postgres config parameters
    shared_buffers = f"{int(postgres_ram * 0.4 / 1e6)}MB"
    effective_cache_size = f"{int(system_ram * 0.5 / 1e6)}MB"
    max_connections = int((workers + max_cron_threads) * db_maxconn * 1.1)
    work_mem = f"{int((system_ram * 0.25) / max_connections / 1e6)}MB"
    maintenance_work_mem = f"{int((system_ram * 0.05) / 1e6)}MB"

    # Create a configuration dictionary with the calculated values
    config = {
        'odoo': {
            'workers': workers,
            'max_cron_threads': max_cron_threads,
            'limit_memory_soft': limit_memory_soft,
            'limit_memory_hard': limit_memory_hard,
            'db_maxconn': db_maxconn
        },
        'postgres': {
            'listen_addresses': '*',
            'shared_buffers': shared_buffers,
            'effective_cache_size': effective_cache_size,
            'max_connections': max_connections,
            'work_mem': work_mem,
            'maintenance_work_mem': maintenance_work_mem
        }
    }

    # Print the calculated values
    for key, value in config.items():
        logger.print_status(f"--- Calculated values for {key} ---")
        for k, v in value.items():
            logger.print_status(f"{k}: {v}")

    odoo_config_file = os.path.join(base_dir, 'config', 'odoo.conf')
    postgres_config_file = os.path.join(base_dir, 'config', 'postgresql.conf')
    _write_config_files(
        postgres_config_file=postgres_config_file,
        odoo_config_file=odoo_config_file,
        config_dict=config,
    )


@app.command(help="Scaffold the Odoo environment")
def scaffold() -> None:
    logger.print_header("Scaffolding Odoo environment")

    files = {
        'config': ['odoo.conf', 'postgresql.conf'],
        'addons': ['requirements.txt'],
        'cache': ['addons_cache.json']
    }

    for key, value in files.items():
        dir_path = os.path.join(base_dir, key)
        dir_existed = os.path.exists(dir_path)
        os.makedirs(dir_path, exist_ok=True)

        # Only set permissions if the directory didn't exist before'
        if not dir_existed:
            try:
                os.chmod(dir_path, 0o755)
            except PermissionError:
                pass

        # Create empty files if they don't exist with the correct permissions
        for file in value:
            file_path = os.path.join(base_dir, key, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("")
                try:
                    os.chmod(file_path, 0o644)
                except PermissionError:
                    pass

    logger.print_success("Odoo environment scaffolding complete")


def _write_config_files(postgres_config_file: str, odoo_config_file: str, config_dict) -> None:
    try:
        logger.print_status("Writing new configuration files")

        # Verify if the file exists
        if not os.path.exists(odoo_config_file):
            raise FileNotFoundError(f"Config file not found: {odoo_config_file}")

        if not os.path.exists(postgres_config_file):
            raise FileNotFoundError(f"Postgres config file not found: {postgres_config_file}")

        # Read the existing configuration file, starting with the odoo config file
        config_override = configparser.ConfigParser()
        config_override.read(odoo_config_file)

        # Ensure the 'options' section exists
        if 'options' not in config_override:
            config_override.add_section('options')

        config_override.set('options', 'workers', str(config_dict['odoo']['workers']))
        config_override.set('options', 'max_cron_threads', str(config_dict['odoo']['max_cron_threads']))
        config_override.set('options', 'limit_memory_soft', str(config_dict['odoo']['limit_memory_soft']))
        config_override.set('options', 'limit_memory_hard', str(config_dict['odoo']['limit_memory_hard']))
        config_override.set('options', 'db_maxconn', str(config_dict['odoo']['db_maxconn']))

        # Write back to the file
        with open(odoo_config_file, 'w') as configfile:
            config_override.write(configfile)

        postgres_config_lines = [
            f"listen_addresses = '{config_dict['postgres']['listen_addresses']}'",
            f"shared_buffers = {config_dict['postgres']['shared_buffers']}",
            f"effective_cache_size = {config_dict['postgres']['effective_cache_size']}",
            f"max_connections = {config_dict['postgres']['max_connections']}",
            f"work_mem = {config_dict['postgres']['work_mem']}",
            f"maintenance_work_mem = {config_dict['postgres']['maintenance_work_mem']}"
        ]

        with open(postgres_config_file, 'w') as configfile:
            configfile.write("\n".join(postgres_config_lines))

        logger.print_success("Odoo and Postgres config files have been successfully written")
    except Exception as e:
        logger.print_error(f"Failed to update configuration files: {e}")


if __name__ == "__main__":
    app()
