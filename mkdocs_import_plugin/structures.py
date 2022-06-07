from typing import List
from urllib.parse import urlparse
from os import path

from pathlib import Path
import requests

import shutil

from .fs import FileSystem

try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit


class File:
    def __init__(self, url: str, path: Path, icon: str = None, hide: List[str] = None):
        self.url = url
        self.path = path
        self.icon = icon
        self.hide = hide

    async def fetch(self, fs: FileSystem) -> 'File':
        if self.is_local():
            return self.copy(fs)
        return self.download(fs)

    def copy(self, fs: FileSystem) -> 'File':
        with open(self.path, 'r') as r:
            with fs.open(self.path, 'w') as w:
                shutil.copyfileobj(r, w)
        return self

    def download(self, fs: FileSystem) -> 'File':
        r = requests.get(self.url, allow_redirects=True)
        with fs.open(self.path, 'w') as f:
            f.write(self.format(r.content.decode('utf-8')))
        return self

    def is_local(self):
        url_parsed = urlparse(self.url)
        if url_parsed.scheme in ('file', ''):
            return path.exists(url_parsed.path)
        return False

    def format(self, content: str) -> str:
        content = content[content.find('#'):]
        header = ""
        if self.icon or self.hide:
            header = "---\n"
        if self.icon:
            header = header + f"icon: {self.icon}\n"
        if self.hide:
            header = header + "hide:\n"
            hides = []
            for hide in self.hide:
                hides.append(f"  - {hide}")
            header = header + "\n".join(hides) + "\n"
        if header:
            header = header + "---\n"
            content = header + "\n" + content
        return content


class Import:
    def __init__(self, name, nav_entry_ptr, file: File):
        self.name = name
        self.nav_entry_ptr = nav_entry_ptr
        self.file = file

    async def imp(self, editor: FileSystem) -> 'Import':
        await self.file.fetch(editor)
        self.nav_entry_ptr[self.name] = str(self.file.path)
        return self

