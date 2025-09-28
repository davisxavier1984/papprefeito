"""
Configuração de logging para a aplicação
"""
import logging
import sys
from typing import Optional

def setup_logger(
    name: str = "papprefeito",
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configura e retorna um logger

    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Formato personalizado das mensagens

    Returns:
        logging.Logger: Logger configurado
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(funcName)s:%(lineno)d - %(message)s"
        )

    # Configurar formatter
    formatter = logging.Formatter(format_string)

    # Configurar handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)

    # Evitar duplicação de logs
    logger.propagate = False

    return logger

# Logger global da aplicação
logger = setup_logger()