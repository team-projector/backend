import json
import pathlib
from io import TextIOWrapper
from typing import Dict, Optional

ASSETS_FOLDER = "assets"


class AssetsProvider:
    """Assets provider."""

    def __init__(self, fspath) -> None:
        """Init provider."""
        self._cwd = pathlib.Path(fspath)
        self._opened_files = []

    def open_file(
        self,
        filename: str,
        mode: str = "rb",
        encoding: str = None,
    ) -> TextIOWrapper:
        """Open file and return a stream."""
        filepath = self._find_path(filename)
        if not filepath:
            raise FileNotFoundError(filename)

        file_handler = open(filepath, mode, encoding=encoding)  # noqa: WPS515
        self._opened_files.append(file_handler)
        return file_handler

    def read_json(self, filename: str) -> Dict:
        """Read json file to dict."""
        return json.loads(self.open_file(filename, mode="r").read())

    def close(self) -> None:
        """Close opened files."""
        for file_handler in self._opened_files:
            if not file_handler.closed:
                file_handler.close()
        self._opened_files.clear()

    def _find_path(self, filename: str) -> Optional[str]:
        """
        Find path.

        :param filename:
        :type filename: str
        :rtype: Optional[str]
        """
        path = self._cwd

        while path.parents:
            pathfile = pathlib.Path(path, ASSETS_FOLDER, filename)
            if pathfile.is_file():
                return pathfile

            path = path.parent

        return None
