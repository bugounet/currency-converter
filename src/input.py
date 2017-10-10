# -*- coding: utf-8 -*-
from converter_exceptions import DialectProblem, FileProblem


class Input(object):
    """ Handles input file opening & returning lines as both parsers need them
    """

    def __init__(self, filename):
        self.client_request, self.change_rates = self.open_file(filename)

    def open_file(self, filename):
        """ Open file by name and return currency dict
        :param filename: File name / path
        :type filename: str

        :return: currency-change rates dict
        :rtype: dict
        """
        try:
            with open(filename, 'r+') as f:
                lines = f.readlines()
                if len(lines) < 1:
                    raise DialectProblem("Input file has not enough data")
                return lines[0], lines[1:]
        except IOError:
            raise FileProblem()
