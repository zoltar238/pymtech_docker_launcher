import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

@dataclass
class Constants:
    COMPOSE_PROJECT_NAME: Optional[str]
    DEPLOYMENT_TARGET: str
    ODOO_VERSION: Optional[str]
    POSTGRES_VERSION: Optional[str]
    ODOO_EXPOSED_PORT: Optional[str]
    ODOO_INTERNAL_PORT: Optional[str]
    ODOO_LOG: Optional[str]
    ODOO_CONFIG: Optional[str]
    ODOO_ADDONS: Optional[str]
    DOMAIN: Optional[str]
    OPTIONAL_WHISPER: Optional[str]
    AUTO_INSTALL_MODULES: Optional[str]
    AUTO_UPDATE_MODULES: Optional[str]
    UPDATE_MODULE_LIST: Optional[str]
    FORCE_UPDATE: Optional[str]
    FORCE_REBUILD: Optional[str]
    AUTO_CREATE_DATABASE: Optional[str]
    BASE_DIR: str
    ADDONS_FOLDER: str
    ENV_FILE: str
    DOCKERFILE_FILE: str
    CACHE_FOLDER: str
    CACHE_CONFIG_FILE: str
    CACHE_ADDONS_FILE: str

    @classmethod
    def from_env(cls, cwd: str) -> 'Constants':
        load_dotenv(f"{cwd}/.env")
        return cls(
            COMPOSE_PROJECT_NAME=os.getenv('COMPOSE_PROJECT_NAME'),
            DEPLOYMENT_TARGET=os.getenv('DEPLOYMENT_TARGET'),
            ODOO_VERSION=os.getenv('ODOO_VERSION'),
            POSTGRES_VERSION=os.getenv('POSTGRES_VERSION'),
            ODOO_EXPOSED_PORT=os.getenv('ODOO_EXPOSED_PORT'),
            ODOO_INTERNAL_PORT=os.getenv('ODOO_INTERNAL_PORT'),
            ODOO_LOG=os.getenv('ODOO_LOG'),
            ODOO_CONFIG=os.getenv('ODOO_CONFIG'),
            ODOO_ADDONS=os.getenv('ODOO_ADDONS'),
            DOMAIN=os.getenv('DOMAIN'),
            OPTIONAL_WHISPER=os.getenv('OPTIONAL_WHISPER'),
            AUTO_INSTALL_MODULES=os.getenv('AUTO_INSTALL_MODULES'),
            AUTO_UPDATE_MODULES=os.getenv('AUTO_UPDATE_MODULES'),
            UPDATE_MODULE_LIST=os.getenv('UPDATE_MODULE_LIST'),
            FORCE_UPDATE=os.getenv('FORCE_UPDATE'),
            FORCE_REBUILD=os.getenv('FORCE_REBUILD'),
            AUTO_CREATE_DATABASE=os.getenv('AUTO_CREATE_DATABASE'),
            BASE_DIR=cwd,
            ADDONS_FOLDER=os.getenv('ODOO_ADDONS') if os.getenv('ODOO_ADDONS') != './addons' else os.path.join(
                cwd, 'addons'),
            ENV_FILE=os.path.join(cwd, ".env"),
            DOCKERFILE_FILE=os.path.join(cwd, "Dockerfile"),
            CACHE_FOLDER=os.path.join(cwd, "cache"),
            CACHE_CONFIG_FILE=os.path.join(cwd, "cache", "config_cache.json"),
            CACHE_ADDONS_FILE=os.path.join(cwd, "cache", "addons_cache.json")
        )


_instance: Optional[Constants] = None


def get_constants(base_dir: str = None) -> Constants:
    """Obtiene o crea la instancia de Constants"""
    global _instance
    if _instance is None:
        if base_dir is None:
            raise ValueError("base_dir must be provided on first call")
        _instance = Constants.from_env(base_dir)
    return _instance
