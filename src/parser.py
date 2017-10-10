# -*- coding: utf-8 -*-
import csv
from price import Price
from decimal import (
    Decimal,
    InvalidOperation
)
from converter_exceptions import (
    DialectProblem,
)

class RequestParser(object):
    """ Request parser is in charge of splitting request line & casting values
    for usage.
    """

    def __init__(self, input):
        elements = input.client_request.strip().split(';')
        if len(elements) != 3:
            raise DialectProblem(
                "Unexpected column count: expected 3 columns: "
                "source_currency;source_price;target_currency"
            )
        self.source_currency = elements[0].upper()
        try:
            self.source_price = Decimal(elements[1])
        except InvalidOperation:
            raise DialectProblem(
                "Invalid source number format. Expected american std notation "
                "for numbers."
            )
        self.target_currency = elements[2].upper()

    def get_price_to_convert(self):
        return Price(self.source_price, self.source_currency)

    def get_target_currency(self):
        return self.target_currency


class AtrealDialect(csv.excel):
    """ Atreal proposed dialect for test problem
    """
    delimiter = ";"


class ChangeRatesParser():
    """ ChangeRatesParser is in charge of reading change table & returning a
    list of usable dicts so that the ChangeTable class can initialize itself.

    """

    def __init__(self, input):
        self.input = input

    def get_rates_lines(self):
        """ Returns parsed lines from bound input class' returned lines
        """
        return self.parse_lines(self.input.change_rates)

    def parse_lines(self, rates_lines):
        """ Given a 3 columns document, it returns the csv iterator that allows
        you to match:

         - first column with "source" key of a virtual CSV
         - second column with "target" key
         - third column with "rate" key

        """
        return csv.DictReader(
            # faked headers becase specified format lacks CSV headers
            ["source;target;rate"] +
            # rate lines
            rates_lines,
            dialect=AtrealDialect
        )

    def split_and_cast_line(self, line):
        """ Fetch each column of given CSV line & return it with few casts &
        checks as a 3 items tuple

        source_currency, target_currency, rate

        :param line: dict or OrderedDict or csv line
        :type line: dict
        """
        source_currency = str(line["source"]).upper()
        if len(source_currency) != 3:
            raise DialectProblem(
                "Unexpected source_currency code: not using ISO 4217 standards."
            )
        target_currency = str(line["target"]).upper()
        if len(target_currency) != 3:
            raise DialectProblem(
                "Unexpected target_currency code: not using ISO 4217 standards."
            )
        rate = line["rate"]
        try:
            rate = Decimal(str(rate))
        except InvalidOperation:
            raise DialectProblem("Expected floating point change rate.")
        return source_currency, target_currency, rate
