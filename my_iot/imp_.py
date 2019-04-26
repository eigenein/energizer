from __future__ import annotations

from importlib.util import module_from_spec, spec_from_loader
from types import ModuleType

from loguru import logger


def create_module(*, name: str, source: str) -> ModuleType:
    """
    Create a module with the given name from the provided source code.
    """
    module: ModuleType = module_from_spec(spec_from_loader(name, loader=None))
    try:
        exec(source, module.__dict__)
    except Exception as e:
        logger.opt(exception=e).error(f'Failed to execute `{name}` module source code.')
    return module
