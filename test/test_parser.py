"""Tests for Coverage.py's code parsing."""

import os, sys, textwrap

sys.path.insert(0, os.path.split(__file__)[0]) # Force relative import for Py3k
from coveragetest import CoverageTest

from coverage.parser import CodeParser


class ParserTest(CoverageTest):
    """Tests for Coverage.py's code parsing."""

    def parse_source(self, text):
        """Parse `text` as source, and return the `CodeParser` used."""
        text = textwrap.dedent(text)
        cp = CodeParser(text)
        cp.parse_source()
        return cp
    
    def test_exit_counts(self):
        cp = self.parse_source("""\
            # check some basic branch counting
            class Foo:
                def foo(self, a):
                    if a:
                        return 5
                    else:
                        return 7
            
            class Bar:
                pass
            """)
        self.assertEqual(cp.exit_counts(), {
            2:1, 3:1, 4:2, 5:1, 7:1, 9:1, 10:1
            })

    def test_try_except(self):
        cp = self.parse_source("""\
            try:
                a = 2
            except ValueError:
                a = 4
            except ZeroDivideError:
                a = 6
            except:
                a = 8
            b = 9
            """)
        self.assertEqual(cp.exit_counts(), {
            1: 1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1
            })
        