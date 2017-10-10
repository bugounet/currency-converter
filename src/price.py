# -*- coding: utf-8 -*-


class Price(object):

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return "%s %s" % (self.amount, self.currency)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.currency == other.currency:
            return self.amount == other.amount
        else:
            # implement me?
            return False