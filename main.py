#!/bin/env python3

"""
A tool for painting and saving Game Boy tiles.

Usage: `python3 gb-tile-painter.py`

Please see: README.md.
"""

from sys import argv, exit

# If we got an argument and it is --help or -h
if len(argv) == 2 and (argv[1] == "--help" or argv[1] == "-h"):
    print(__doc__) # Print the docstring
    exit(0) # And exit

from MainWindow import MainWindow

if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()