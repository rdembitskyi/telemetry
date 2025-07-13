import configparser
import logging
from pathlib import Path

# Set up a logger for this module
log = logging.getLogger(__name__)


def load_config() -> configparser.ConfigParser:
    """
    Finds and loads the 'config.ini' file from the project root.

    This function robustly locates the configuration file by navigating up
    from the current script's location. It assumes a standard project
    structure where the script is inside a source directory (e.g., 'src',
    'app', or 'telemetry_sink') and 'config.ini' is in the parent directory.

    Raises:
        FileNotFoundError: If 'config.ini' cannot be found at the expected location.
        configparser.Error: If the file is found but cannot be parsed.

    Returns:
        A ConfigParser object populated with the settings.
    """
    try:
        script_dir = Path(__file__).resolve().parent.parent
        project_root = script_dir.parent
        config_path = project_root / "config.ini"

        log.info(f"Attempting to load configuration from: {config_path}")

        if not config_path.exists():
            log.critical(f"Configuration file not found at: {config_path}")
            raise FileNotFoundError(f"Required configuration file 'config.ini' not found.")

        # 4. Initialize the parser and read the file.
        config = configparser.ConfigParser()
        config.read(config_path)

        log.info("Configuration file loaded successfully.")
        return config

    except configparser.Error as e:
        log.critical(f"Failed to parse the configuration file. Please check for syntax errors. Error: {e}")
        raise
    except Exception as e:
        log.critical(f"An unexpected error occurred while loading the configuration: {e}")
        raise
