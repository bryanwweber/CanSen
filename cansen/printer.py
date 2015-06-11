# Standard Libraries
import sys

# Create a string to use as a divider. Use a default column width of
# 80 chars.
divider = '*'*80


class Tee(object):
    """Write to screen and text output file"""

    def __init__(self, name, mode):
        """Initialize output.

        :param name:
            Output file name.
        :param mode:
            Read/Write mode of the output file.
        """

        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def close(self):
        """Close output file and restore standard behavior"""

        if self.stdout is not None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.file is not None:
            self.file.close()
            self.file = None

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def __del__(self):
        self.close()
