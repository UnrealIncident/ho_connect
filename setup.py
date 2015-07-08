from distutils.core import setup
import py2exe

setup(
    options = {'py2exe': {'bundle_files': 1}},
    console = [{'script': "test_match.py", 'dest_base': 'connect'}],
    zipfile = None,
)

setup(
    options = {'py2exe': {'bundle_files': 1}},
    console = [{'script': "dump_server.py", 'dest_base': 'host'}],
    zipfile = None,
)