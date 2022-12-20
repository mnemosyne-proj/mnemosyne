#
# html_statistics.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage


# The statistics page.

class MyHtmlStatistics(HtmlStatisticsPage):

    name = "My html staticsics"
         
    def prepare_statistics(self, variant):
        card = self.review_controller().card
        self.html = """<html<body>
        <style type="text/css">
        table { height: 100%;
                margin-left: auto; margin-right: auto;
                text-align: center}
        body  { background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head><table><tr><td>"""  
        self.html += "There are lies, damn lies and statistics."
        self.html += "</td></tr></table></body></html>"


# Wrap it into a Plugin and then register the Plugin.

class MyHtmlStatisticsPlugin(Plugin):
    name = "Html statistics example"
    description = "Example plugin for html statistics"
    components = [MyHtmlStatistics]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(MyHtmlStatisticsPlugin)
