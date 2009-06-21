#
# html_statistics.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage


# The statistics page.

class HtmlStatistics(StatisticsPage):

    name = "Html staticsics"
        
    def prepare(self, variant):
        card = self.ui_controller_review().card
        self.data = """<html<body>
        <style type="text/css">
        table { height: 100%;
                margin-left: auto; margin-right: auto;
                text-align: center}
        body  { background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head><table><tr><td>"""
        
        self.data += "There are lies, damn lies and statistics."

        self.data += "</td></tr></table></body></html>"


# Wrap it into a Plugin and then register the Plugin.

class HtmlStatisticsPlugin(Plugin):
    name = "Html statistics example"
    description = "Example plugin for html statistics"
    components = [HtmlStatistics]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(HtmlStatisticsPlugin)

