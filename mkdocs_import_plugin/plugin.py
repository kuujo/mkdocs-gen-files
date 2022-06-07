from typing import Dict, List, Tuple
from sys import version_info
from pathlib import Path
import tempfile

from mkdocs.config import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files

import asyncio
import tqdm

from .fs import FileSystem
from .structures import File, Import

try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit


class ImportPlugin(BasePlugin):
    config_scheme = tuple()

    def __init__(self):
        self._dir = tempfile.TemporaryDirectory(prefix="mkdocs_import_plugin_")

    def on_files(self, files: Files, config: Config) -> Files:
        nav: List[Dict] = config.get('nav')
        imports = get_imports(nav)
        fs = FileSystem(files, config, self._dir.name)
        asyncio_run(batch_import(fs, imports))
        return fs.files

    def on_post_build(self, config: Config):
        self._dir.cleanup()


def _parse_import(name: str, value: str, path: Path) -> Tuple[str, Path]:
    """Parses !import statements"""
    elems = value.split(' ')[1:]
    if len(elems) == 1:
        return value, path / f"{name}.md"
    return elems[0], Path(elems[1])


def get_imports(nav: List[Dict], path: Path = Path('')) -> List[Import]:
    imports: List[Import] = []
    for index, entry in enumerate(nav):
        if isinstance(entry, str):
            continue
        (name, value), = entry.items()
        if type(value) is list:
            imports += get_imports(value, path / name)
        elif value.startswith("!import"):
            import_url, import_path = _parse_import(name, value, path)
            imports.append(Import(name, nav[index], File(url=import_url, path=import_path)))
    return imports


async def batch_import(fs: FileSystem, imports: List[Import]) -> None:
    if not imports:
        return None
    longest_desc = max([len(f"✅ Downloaded {imp.file.url}") for imp in imports])
    progress_bar = tqdm.tqdm(total=len(imports), desc=" " * longest_desc)
    for imp_async in asyncio.as_completed([imp.imp(fs) for imp in imports]):
        imp = await imp_async
        progress_bar.set_description(f"✅ Downloaded {imp.file.url}".ljust(longest_desc))
        progress_bar.update()


def asyncio_run(futures) -> None:
    if (version_info.major == 3 and version_info.minor > 6) or (version_info.major > 3):
        asyncio.run(futures)
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(futures)