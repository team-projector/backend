import getopt
import glob
import os
import re
import sys


class FuzzyChecker:
    has_error = False
    show_log = False
    path = ''
    file_pattern = '*.po'
    fuzzy_reg = r'(#\W*fuzzy$)'

    def __init__(self, sys_arg=None):
        self.set_options(sys_arg)

    def __str__(self):
        return f'Fuzzy checker: {self.path}'

    def run(self) -> bool:
        return bool(self._run())

    def _run(self):
        self.log(f'Root path: {self.path}')
        files = self.get_files()

        if not files:
            return

        self.check_files(files)

        return self.has_error

    def get_files(self):
        found_files = []
        for root, dirs, files in os.walk(os.path.normpath(self.path)):
            found_files.extend(glob.glob(os.path.join(os.path.abspath(root), self.file_pattern)))

        message = 'Found files:\n' if found_files else 'Files not found'
        files = '\n'.join(found_files)
        self.log(f'{message}{files}')

        return found_files

    def check_files(self, files):
        for file in files:
            self.check_file(file)

    def check_file(self, file_path):
        self.log(f'Checking: {file_path}')
        with open(file_path, 'r') as f:
            content = f.readlines()

            if not self.has_match(' '.join(content)):
                return

            for i, line in enumerate(content):
                self.check_line(line, i + 1, file_path)

    def check_line(self, line, index, file_path):
        if not self.has_match(line):
            return

        self.has_error = True
        self.log(f'{file_path}:{index} -> {line.strip()}', True)

    def has_match(self, source):
        return bool(re.search(self.fuzzy_reg, source, flags=re.M))

    def log(self, value, force=False):
        if self.show_log or force:
            print(value)

    def set_options(self, sys_arg):
        if not sys_arg:
            return

        opts, _ = getopt.getopt(sys_arg, 'l', ['path='])
        for k, v in opts:
            if k == '--path' and v:
                self.path = v
            elif k == '-l':
                self.show_log = True

        self.path = os.path.abspath(self.path)


def main() -> None:
    sys.exit(FuzzyChecker(sys.argv[1:]).run())


if __name__ == "__main__":
    main()
