from pathlib import Path
import requests

from .fs import FileSystem

try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit


class File:
    def __init__(self, url: str, path: Path):
        self.url = url
        self.path = path

    async def download(self, editor: FileSystem) -> 'File':
        r = requests.get(self.url, allow_redirects=True)
        with editor.open(self.path, 'w') as f:
            f.write(_strip_badges(r.content.decode('ascii')))
        return self


class Import:
    def __init__(self, section, nav_entry_ptr, file: File, alias: str):
        self.section = section
        self.nav_entry_ptr = nav_entry_ptr
        self.file = file
        self.alias = alias

    async def imp(self, editor: FileSystem) -> 'Import':
        await self.file.download(editor)
        self.nav_entry_ptr[self.section] = self.alias
        return self


def _strip_badges(content: str) -> str:
    return content[content.find('#'):]

