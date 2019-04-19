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

    def __init__(self):
        self.set_options()

    def run(self):
        try:
            self._run()
        except:
            return 1

    def _run(self):
        files = self.get_files()

        if not files:
            return

        self.check_files(files)

        if self.has_error:
            raise Exception()

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
        self.log(f'{file_path}:{index}: {line.strip()}', True)

    def has_match(self, source):
        return bool(re.search(self.fuzzy_reg, source, flags=re.M))

    def log(self, value, force=False):
        if self.show_log or force:
            print(value)

    def set_options(self):
        opts, _ = getopt.getopt(sys.argv[1:], 'l', ['path='])
        for k, v in opts:
            if k == '--path' and v:
                self.path = v
            elif k == '-l':
                self.show_log = True

        self.path = os.path.abspath(self.path)
        self.log(f'Root path: {self.path}')


def main():
    sys.exit(FuzzyChecker().run())


if __name__ == "__main__":
    main()
