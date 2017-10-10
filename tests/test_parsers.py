# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import Mock
from decimal import Decimal

from converter_exceptions import DialectProblem
from price import Price


class ChangeRatesParserTestCase(TestCase):
    def test_direct_change_rate_identification(self):
        # assuming
        from parser import ChangeRatesParser

        mocked_input = Mock()
        mocked_input.change_rates = ["EUR;GBP;1.5", "USD;SEK;12"]

        parser = ChangeRatesParser(mocked_input)


        # when
        lines = parser.get_rates_lines()


        # then
        expectations = [
            {
                "source": "EUR",
                "target": "GBP",
                "rate": "1.5"
            },
            {
                "source": "USD",
                "target": "SEK",
                "rate": "12"
            }
        ]

        for idx, csv_line in enumerate(lines):
            self.assertEqual(dict(csv_line), expectations[idx])

    def test_split_and_cast_line(self):
        # assuming
        mocked_input = Mock()
        from parser import ChangeRatesParser
        parser = ChangeRatesParser(mocked_input)

        # when
        result = parser.split_and_cast_line(
            {"source": "aBc", "target": "DeF", "rate": "123"}
        )

        # then
        self.assertEqual(result, ("ABC", "DEF", Decimal("123")))

    def test_split_and_cast_line_meets_non_iso_data(self):
        from parser import ChangeRatesParser
        from converter_exceptions import DialectProblem

        # assuming
        mocked_input = Mock()
        parser = ChangeRatesParser(mocked_input)

        # when
        with self.assertRaises(DialectProblem) as e:
            parser.split_and_cast_line(
                {"source": "aBcd", "target": "DeF", "rate": "123"}
            )
            # then
            self.assertEqual(
                e.message,
                "Unexpected source_currency code: not using ISO 4217 standards."
            )

        # when
        with self.assertRaises(DialectProblem) as e:
            parser.split_and_cast_line(
                {"source": "aBc", "target": "DF", "rate": "123"}
            )
            # then
            self.assertEqual(
                e.message,
                "Unexpected target_currency code: not using ISO 4217 standards."
            )

    def test_split_and_cast_line_with_non_american_numbers_notation(self):
        "Expected floating point change rate."
        from parser import ChangeRatesParser
        from converter_exceptions import DialectProblem

        # assuming
        mocked_input = Mock()
        parser = ChangeRatesParser(mocked_input)

        # when
        with self.assertRaises(DialectProblem) as e:
            parser.split_and_cast_line(
                {"source": "ABC", "target": "DEF", "rate": "123,24"}
            )
            # then
            self.assertEqual(
                e.message,
                "Expected floating point change rate."
            )


class RequestParserTestCase(TestCase):

    def test_get_source_price(self):
        from parser import RequestParser
        # assuming
        mocked_input = Mock()
        mocked_input.client_request = "USD;20.1;EUR\r\n"

        # when
        parser = RequestParser(mocked_input)

        #then
        self.assertEqual(parser.source_currency, "USD")
        self.assertEqual(parser.source_price, Decimal("20.1"))
        self.assertEqual(parser.target_currency, "EUR")

    def test_get_price_to_convert(self):
        from parser import RequestParser
        # assuming
        mocked_input = Mock()
        mocked_input.client_request = "Usd;20.3;Eur\r\n"

        # when
        parser = RequestParser(mocked_input)
        #then
        self.assertEqual(
            parser.get_price_to_convert(),
            Price(Decimal("20.3"), "USD")
        )

    def test_get_target_currency(self):
        from parser import RequestParser
        # assuming
        mocked_input = Mock()
        mocked_input.client_request = "UsD;20.23;EuR\r\n"

        # when
        parser = RequestParser(mocked_input)

        # then
        self.assertEqual(parser.get_target_currency(), "EUR")

    def test_parsing_too_few_args(self):
        from parser import RequestParser
        # assuming
        mocked_input = Mock()

        # when too few args
        mocked_input.client_request = "USD;20.1\r\n"

        # then an exception is raised
        with self.assertRaises(DialectProblem) as e:
            RequestParser(mocked_input)
            self.assertEqual(
                e.message,
                "Unexpected column count: expected 3 columns: "
                "source_currency;source_price;target_currency"
            )

    def test_parsing_too_many_args(self):
        from parser import RequestParser
        # assuming
        mocked_input = Mock()

        # when too many args
        mocked_input.client_request = "USD;20.00;EUR;test\r\n"

        # then an exception is also raised
        with self.assertRaises(DialectProblem) as e:
            RequestParser(mocked_input)
            self.assertEqual(
                e.message,
                "Unexpected column count: expected 3 columns: "
                "source_currency;source_price;target_currency"
            )
    def test_parsing_non_decimal_amount(self):

        from parser import RequestParser
        # assuming
        mocked_input = Mock()

        # when too many args
        mocked_input.client_request = "USD;20,1;EUR;test\r\n"

        # then an exception is also raised
        with self.assertRaises(DialectProblem) as e:
            RequestParser(mocked_input)
            self.assertEqual(
                e.message,
                "Invalid source number format. Expected american std notation "
                "for numbers."
            )
