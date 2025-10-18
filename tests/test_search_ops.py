import os
import tempfile
from src.core import search_ops


def test_find_in_file_true_false():
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, 'b.txt')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write('findme')
        assert search_ops.find_in_file(f, 'findme')
        assert not search_ops.find_in_file(f, 'absent')
