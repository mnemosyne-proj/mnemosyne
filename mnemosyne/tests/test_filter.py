#
# test_filter.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne.libmnemosyne.filter import Filter

class TestFilter:
    
    @raises(NotImplementedError)
    def test(self):
        f = Filter(None)
        f.run("")
