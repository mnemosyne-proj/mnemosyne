#
# test_util_functions.py - Mike Appleby <mike@peacecorps.org.cv>
#

import os
import shutil

from mnemosyne.libmnemosyne.utils import *

class TestUtilFunctions(object):

    def test_numeric_string_cmp_1(self):
        s1 = "abc123"
        s2 = "abc1000"
        assert numeric_string_cmp_key(s1) < numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_2(self):
        s1 = "Category 9"
        s2 = "Category 11"
        assert numeric_string_cmp_key(s1) < numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_3(self):
        s1 = "3 blind mice"
        s2 = "3 blind pigs"
        assert numeric_string_cmp_key(s1) < numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_3(self):
        s1 = "3 blind mice"
        s2 = "13 blind mice"
        assert numeric_string_cmp_key(s1) < numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_4(self):
        s1 = "a"
        s2 = "b"
        assert numeric_string_cmp_key(s1) < numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_5(self):
        s1 = "a123"
        s2 = "a123"
        assert numeric_string_cmp_key(s1) == numeric_string_cmp_key(s2)

    def test_numeric_string_cmp_6(self):
        s1 = "xyz 77"
        s2 = "xyz 42"
        assert numeric_string_cmp_key(s1) > numeric_string_cmp_key(s2)

    def test_contract_windows(self):
        assert contract_path("C:\\a\\b", "C:\\a") == "b"
        #assert contract_path("C:\\a\\b", "c:\\a") == "b"

    def test_mangle(self):
        for name in [mangle("1aa"), mangle("a!@#$% ^&*(){}{a"),
                     mangle("a\xac\\u1234\\u20ac\\U00008000")]:
            C = type(name, (self.__class__, ),
                 {"name": 1})

    def test_copy(self):
        assert copy_file_to_dir("/home/joe/test.py", "/home/joe") == "test.py"
        assert copy_file_to_dir("/home/joe/test.py", "/home/joe/") == "test.py"
        assert copy_file_to_dir("/home/joe/a/test.py", "/home/joe") == "a/test.py"
        assert copy_file_to_dir("/home/joe/a/test.py", "/home/joe/") == "a/test.py"

    def test_strip_tags(self):
        assert strip_tags("""<img = "">""") == ""

    def test_filesystem(self):
        is_filesystem_case_insensitive()


