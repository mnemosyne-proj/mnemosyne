#
# test_util_functions.py - Mike Appleby <mike@peacecorps.org.cv>
#

from mnemosyne.libmnemosyne.utils import *

class TestUtilFunctions:

    def test_numeric_string_cmp_1(self):
        s1 = "abc123"
        s2 = "abc1000"
        assert numeric_string_cmp(s1, s2) < 0

    def test_numeric_string_cmp_2(self):
        s1 = "Category 9"
        s2 = "Category 11"
        assert numeric_string_cmp(s1, s2) < 0

    def test_numeric_string_cmp_3(self):
        s1 = "3 blind mice"
        s2 = "3 blind pigs"
        assert numeric_string_cmp(s1, s2) < 0

    def test_numeric_string_cmp_3(self):
        s1 = "3 blind mice"
        s2 = "13 blind mice"
        assert numeric_string_cmp(s1, s2) < 0

    def test_numeric_string_cmp_4(self):
        s1 = "a"
        s2 = "b"
        assert numeric_string_cmp(s1, s2) < 0

    def test_numeric_string_cmp_5(self):
        s1 = "a123"
        s2 = "a123"
        assert numeric_string_cmp(s1, s2) == 0

    def test_numeric_string_cmp_6(self):
        s1 = "xyz 77"
        s2 = "xyz 42"
        assert numeric_string_cmp(s1, s2) > 0
