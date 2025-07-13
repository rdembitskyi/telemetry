import configparser
import logging
from pathlib import Path


def load_config() -> configparser.ConfigParser:
    """
    Loads configuration from 'config.ini' located in the project root.

    This function robustly finds the config file by navigating up from the
    current script's location. It assumes the project root is one level
    above the 'src' directory where the script resides.

    Returns:
        A ConfigParser object populated with the settings.

    Raises:
        FileNotFoundError: If the config file cannot be found.
    """
    try:
        script_dir = Path(__file__).resolve().parent.parent
        project_root = script_dir.parent
        config_path = project_root / "config.ini"

        if not config_path.exists():
            logging.error(f"Configuration file not found at expected path: {config_path}")
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        config = configparser.ConfigParser()
        config.read(config_path)
        logging.info(f"Successfully loaded configuration from {config_path}")
        return config

    except Exception as e:
        logging.error(f"Failed to load or parse configuration: {e}")
        # Re-raising the exception allows the main application to handle it.
        raise
