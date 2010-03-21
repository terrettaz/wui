from django.test import TestCase
from wui.settings import *
from wui.api.js_utils import *
from pprint import pprint
class JSParserTest(TestCase):

    def test_jsparser(self):
        
        parser = JSParser(WUI_JS_DIR + '/wui.js')
        parser.parse()
        pprint(parser.build_documentation())

__test__ = {"doctest": """
    
"""}

