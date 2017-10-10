# -*- coding: utf-8 -*-
from unittest import TestCase

from decimal import Decimal


class ChangeTableTestCase(TestCase):
    def test_direct_change_rate_identification(self):
        # assuming
        from change import ChangeRateTable

        change_table = ChangeRateTable(None)
        change_table.tree = {
            "EUR": {
                "USD": Decimal("1.59"),
            }
        }

        # when
        result = change_table._browse_tree("EUR", "USD")

        # then
        self.assertEqual(result, [
            Decimal("1.59"),
        ])

    def test_1_step_change(self):
        # assuming
        from change import ChangeRateTable

        change_table = ChangeRateTable(None)
        change_table.tree = {
            "EUR": {
                "BOB": Decimal("1.59"),
            },
            "BOB": {
                "USD": Decimal("1.3"),
            }
        }

        # when
        result = change_table._browse_tree("EUR", "USD")

        # then
        self.assertEqual(result, [
            Decimal("1.59") * Decimal("1.3"),
        ])

    def test_infinite_loop_break(self):
        # assuming
        from change import ChangeRateTable

        change_table = ChangeRateTable(None)
        # there is a loop --> eur -> usd -> gbp -> eur
        # the test checks you don't loop for ever
        change_table.tree = {
            "EUR": {
                "USD": Decimal("1.59"),
            },
            "USD": {
                "GBP": Decimal("1.3"),
            },
            "GBP": {
                "EUR": Decimal("1.4")
            }
        }
        testing_set = set()

        # when
        # there should be no rate available
        result = change_table._browse_tree("EUR", "JPY", testing_set)

        # then
        self.assertEqual(result, [])
        # and
        self.assertEqual(testing_set, set(["EUR-JPY", "USD-JPY", "GBP-JPY"]))

    def test_inverse_change_rate(self):
        # assuming
        from parser import ChangeRatesParser
        from change import ChangeRateTable

        class MockChangeRatesParser(ChangeRatesParser):
            def get_rates_lines(self):
                return [{"source":"EUR", "target": "JPY", "rate":"2.0"}]

        parser = MockChangeRatesParser(None)
        change_table = ChangeRateTable(parser)
        change_table.initialize_tree()

        # when
        result = change_table._browse_tree("JPY", "EUR")

        # then
        self.assertEqual(result, [
            Decimal("0.5"),
        ])

    def atreal_test(self):
        pass
    """EUR;CHF;1.14651
USD;GBP;0.742190
USD;XPF;100.714
GBP;XPF;135.704
XPF;CHF;0.00960574
"""