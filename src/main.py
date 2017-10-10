# -*- coding: utf-8 -*-
import sys

from input import Input
from change import ChangeRateTable
from parser import RequestParser, ChangeRatesParser


if __name__ == "__main__":
    input = Input(sys.argv[1])

    parser = RequestParser(input)
    source_price = parser.get_price_to_convert()
    target_currency = parser.get_target_currency()

    change_table = ChangeRateTable(ChangeRatesParser(input))
    change_table.initialize_tree()

    # import ipdb ; ipdb.set_trace()
    changed_price = change_table.change_price(source_price, target_currency)

    print(
        "{source} when changed into {target_currency} is worth {result}".format(
            source=source_price,
            target_currency=target_currency,
            result=changed_price
        )
    )