# -*- coding: utf-8 -*-
""" Program explanation:

Problem asks to get the lowest end-rate for a given change.

Let's say we want to change a price from currency AAA to currency CCC,
we can either change it directly using AAA to CCC change rate ; but
AAA->BBB->CCC must also be tried to make sur it can't be cheaper.

At first sight I see two possible implementations:

- pre-compute change rates from all currency to all currency and store the
cheapest possibility.

- Browse the whole change tree

I chose to stick to the second plan for mainly two reasons:
* I don't need to run this application on many inputs so investing time & memory
into pre-computing a whole table is futile

* As I have access to no local database and as I want to reduce my memory
fingerprint a little bit so I won't pre-compute this exhaustive change table
just to drop a print and shut the program-down


Well, then it's a bit time consuming but an exhaustive walk through the change
tree will give us the answer.

The tree is composed as follows:



      BBB
    /
AAA - CCC

      CCC
    /
BBB
    \
      AAA

CCC - BBB
    \
      AAA

I will browse all nodes and keep a set of met-curencies.
For each node, either I arrive on target-currency (then I save found change rate)
OR I haven't fount it yet and try another change-rate (then I hope to find it).

"""
from decimal import Decimal

from price import Price


class ChangeRateTable(object):
    """ Change table returns changed price for input price
    """
    def __init__(self, parser, precision = Decimal("0.01")):
        self.change_amount_precision = precision
        self.parser = parser
        self.tree = None

    def initialize_tree(self):
        self.tree = self.create_change_tree()

    def create_change_tree(self):
        rates = self.parser.get_rates_lines()

        tree = {}
        for line in rates:
            parts = self.parser.split_and_cast_line(line)
            # explode parts into variables
            source_currency, target_currency, rate = parts

            node = tree.get(source_currency, {})
            node[target_currency] = rate
            tree[source_currency] = node

            # if the main way already exists, do not override it. It exists and
            # will be more important than the "inverted" change we will guess
            # in the following 3 lines of code.

            node = tree.get(target_currency, {})
            node[source_currency] = node.get(
                target_currency, Decimal(1) / rate
            )
            tree[target_currency] = node

        return tree

    def change_price(self, source_price, target_currency):
        possible_rates = self._browse_tree(source_price.currency, target_currency)
        if len(possible_rates) == 0:
            return source_price
        min_rate = min(*possible_rates)
        target_amount = (source_price.amount * min_rate).quantize(
            self.change_amount_precision
        )
        return Price(target_amount, target_currency)

    def _browse_tree(self, source_currency, target_currency, _met_change_paths=None):
        """ For each unmet currency:
        - either it's in the file (i.e. in the table's root), then save the rate

        - or it's not then try all sub-currencies from node then apply node's
            rate onto resulting change rates.

        :param source_currency: Source currency (changes on recursion)
        :type source_currency: str

        :param target_currency: Target currency (doesn't change in recursion)
        :type target_currency: str

        :param _met_change_paths: Set of already met currencies. It takes
                                advantage of mutable objects properties to be
                                updated internally by recusrive calls of the
                                function. Don't set it yourself, the function
                                will do it for you.
        :type _met_change_paths: set

        :return: list of rates
        :rtype: list<Decimal>
        """
        print("compute change from ", source_currency, "to ", target_currency)
        possible_rates = []

        if _met_change_paths is None:
            _met_change_paths = set()

        node = self.tree.get(source_currency, {})

        for currency in node.keys():
            print("Sub rate for ", source_currency," to ", currency, '(target ', target_currency, target_currency == currency, ")")
            change_key = self.get_change_key(currency, target_currency)

            if currency == target_currency:
                print("found target currency, retruning rate", node[currency])
                # direct change rate, just store it.
                possible_rates.append(node[currency])
                # _met_change_paths.add(change_key)
                continue

            if change_key in _met_change_paths:
                print("already-met ",change_key, ", skipping")
                # already met. Just skip it
                continue

            rate = node[currency]
            _met_change_paths.add(change_key)

            # recurse
            sub_rates = self._browse_tree(
                currency,
                target_currency,
                _met_change_paths
            )
            for sub_rate in sub_rates:
                possible_rates.append(rate * sub_rate)


        return possible_rates

    def get_change_key(self, source, target):
        return "{}-{}".format(source, target)