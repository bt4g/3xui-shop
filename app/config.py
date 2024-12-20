from dataclasses import dataclass
from pathlib import Path

from environs import Env
from marshmallow.validate import OneOf

BASE_DIR = Path(__file__).resolve().parent

# Default values for database
DEFAULT_DB_NAME = "bot_database"

# Default values for logging configurations
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_LOG_DIR = "./logs"
DEFAULT_LOG_ARCHIVE_FORMAT = "zip"


@dataclass
class BotConfig:
    """
    Configuration for the Telegram bot.

    Attributes:
        TOKEN (str): API token for the Telegram bot.
        DEV_ID (int | None): Developer ID (user ID) for notifications.
        SUPPORT_ID (int): Support ID (user ID) for support.
    """

    TOKEN: str
    DEV_ID: int | None
    SUPPORT_ID: int


@dataclass
class XUIConfig:
    """
    Configuration for XUI.

    Attributes:
        HOST (str): Host URL for the XUI service.
        USERNAME (str): Username for XUI authentication.
        PASSWORD (str): Password for XUI authentication.
        TOKEN (str | None): API token for XUI.
        SUBSCRIPTION (str): Base URL for XUI subscription.
    """

    HOST: str
    USERNAME: str
    PASSWORD: str
    TOKEN: str | None
    SUBSCRIPTION: str


@dataclass
class DatabaseConfig:  # TODO: Add support for different drivers
    """
    Configuration for the database.

    Attributes:
        HOST (str | None): Host address of the database server.
        PORT (int | None): Port number for the database server.
        USERNAME (str | None): Username for database authentication.
        PASSWORD (str | None): Password for database authentication.
        NAME (str): Name of the database to connect to.
    """

    HOST: str | None
    PORT: int | None
    USERNAME: str | None
    PASSWORD: str | None
    NAME: str

    def url(self, driver: str = "sqlite+aiosqlite") -> str:
        """
        Generates a database connection URL using the provided driver,
        username, password, host, port, and database name.

        Args:
            driver (str): Driver to use for the connection. Defaults to "sqlite+aiosqlite".

        Returns:
            str: Generated connection URL.
        """
        if driver.startswith("sqlite"):
            return f"{driver}:///./{self.NAME}.db"
        return f"{driver}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class LoggingConfig:
    """
    Configuration for logging.

    Attributes:
        LEVEL (str): Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        FORMAT (str): Format string for log messages.
        DIR (str): Directory where log files are stored.
        ARCHIVE_FORMAT (str): Archive format for log archiving.
    """

    LEVEL: str
    FORMAT: str
    DIR: str
    ARCHIVE_FORMAT: str


@dataclass
class Config:
    """
    Main configuration class.

    Attributes:
        bot (BotConfig): Bot configuration.
        xui (XUIConfig): XUI configuration.
        database (DatabaseConfig): Database configuration.
        logging (LoggingConfig): Logging configuration.
    """

    bot: BotConfig
    xui: XUIConfig
    database: DatabaseConfig
    logging: LoggingConfig


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config: Application configuration.
    """
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env.str("BOT_TOKEN"),
            DEV_ID=env.int("BOT_DEV_ID", None),
            SUPPORT_ID=env.int("BOT_SUPPORT_ID"),
        ),
        xui=XUIConfig(
            HOST=env.str("XUI_HOST"),
            USERNAME=env.str("XUI_USERNAME"),
            PASSWORD=env.str("XUI_PASSWORD"),
            TOKEN=env.str("XUI_TOKEN", None),
            SUBSCRIPTION=env.str("XUI_SUBSCRIPTION"),
        ),
        database=DatabaseConfig(
            HOST=env.str("DB_HOST", None),
            PORT=env.int("DB_PORT", None),
            USERNAME=env.str("DB_USERNAME", None),
            PASSWORD=env.str("DB_PASSWORD", None),
            NAME=env.str("DB_NAME", DEFAULT_DB_NAME),
        ),
        logging=LoggingConfig(
            LEVEL=env.str("LOG_LEVEL", DEFAULT_LOG_LEVEL),
            FORMAT=env.str("LOG_FORMAT", DEFAULT_LOG_FORMAT),
            DIR=env.str("LOG_DIR", DEFAULT_LOG_DIR),
            ARCHIVE_FORMAT=env.str(
                "LOG_ARCHIVE_FORMAT",
                DEFAULT_LOG_ARCHIVE_FORMAT,
                validate=OneOf(["zip", "gz"], error="LOG_ARCHIVE_FORMAT must be one of: {choices}"),
            ),
        ),
    )
