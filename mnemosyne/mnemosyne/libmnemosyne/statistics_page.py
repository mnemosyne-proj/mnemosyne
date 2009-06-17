#
# statistics_page.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class StatisticsPage(Component):

    """A self-contained piece of statistical information, typically displayed
    in the GUI as a page in a tabbed widget.

    Each StatisticsPage can have several 'variants', e.g. displaying the
    number of scheduled cards either for next week or for next month.

    A StatisticsPage can also set some hints to indicate how it prefers the
    data to be displayed in the GUI, through variables like 'plot_type',
    'title', 'xlabel', 'ylabel, ... . See the source for more details.

    For each StatisticsPage, there will be an associated widget (HTML browser,
    plotting widget, custom widget, ... ) that is in charge of displaying the
    information from that StatisticsPage. The widget can be registered in the
    component manager as an widget component 'used_for' a particular
    StatisticsPage, but if no such information is available, the GUI toolkit
    should make an educated guess.


    """
    
    component_type = "statistics_page"    
    instantiate = Component.LATER

    name = ""
    variants = [] # [(variant_id, variant_name)]
        
    def __init__(self):
        self.data = None
        
        # Relevant for graphs.
        self.plot_type = "" # barchart, histogram, piechart
        self.title = ""
        self.xlabel = ""
        self.ylabel = ""
        self.xticks = []
        self.xticklabels = []
        
        # Relevant for histograms. TODO: needed?
        self.range = []
        self.bins = -1
        
        # Other hints should be collected here:
        self.extra_hints = {}

    def prepare(self, variant_id):

        """This method calculates the data for the requested variant and sets
        the approriate hints to be picked up by the corresponding widget.

        """
        
        raise NotImplementedError
        
