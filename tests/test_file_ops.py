import os
import tempfile
from src.core import file_ops


def test_list_dir_and_formatting():
    with tempfile.TemporaryDirectory() as td:
        # create files and a dir
        f1 = os.path.join(td, 'a.txt')
        with open(f1, 'w') as f:
            f.write('hello')
        os.mkdir(os.path.join(td, 'sub'))
        items = file_ops.list_dir(td)
        names = [i[0] for i in items]
        assert 'a.txt' in names
        assert 'sub' in names
        # size formatting
        assert 'bytes' in file_ops.format_size(10)
        assert file_ops.format_mtime(None) == ''
