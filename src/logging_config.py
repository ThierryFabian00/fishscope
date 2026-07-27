import logging

from src.security import FiltroSegredos


def configurar_logging(verbose: bool = False) -> None:
    nivel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    for manipulador in logging.getLogger().handlers:
        manipulador.addFilter(FiltroSegredos())
