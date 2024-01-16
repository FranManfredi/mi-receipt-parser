
import json
import re
import dateutil.parser
from difflib import get_close_matches


def add_card_number(payment_method_line):
    numbers = re.findall(r'\d+', payment_method_line)
    joined_numbers = ''.join(numbers)
    return joined_numbers


class Receipt(object):
    """ Company receipt to be parsed """

    def __init__(self, config, raw):
        """
        :param config: ObjectView
            Config object
        :param raw: [] of str
            Lines in file
        """

        self.config = config
        self.company = None
        self.date = None
        self.total = None
        self.payment_method = None
        self.lines = raw
        self.normalize()
        self.parse()

    def normalize(self):
        """
        :return: void
            1) strip empty lines
            2) convert to lowercase
            3) encoding?

        """

        self.lines = [
            line.lower() for line in self.lines if line.strip()
        ]

    def parse(self):
        """
        :return: void
            Parses obj data
        """

        self.company = self.parse_company()
        self.date = self.parse_date()
        self.total = self.parse_total()
        self.payment_method = self.parse_payment_method()

    def fuzzy_find(self, keyword, accuracy=0.6):
        """
        :param keyword: str
            The keyword string to look for
        :param accuracy: float
            Required accuracy for a match of a string with the keyword
        :return: str
            Returns the first line in lines that contains a keyword.
            It runs a fuzzy match if 0 < accuracy < 1.0
        """

        for line in self.lines:
            words = line.split()
            # Get the single best match in line
            matches = get_close_matches(keyword, words, 1, accuracy)
            if matches:
                return line

    def parse_date(self):
        """
        :return: date
            Parses data
        """

        for line in self.lines:
            match = re.search(self.config.date_format, line)
            if match:  # We"re happy with the first match for now
                # validate date using the dateutil library (see: https://dateutil.readthedocs.io/)
                date_str = match.group(1)
                date_str = date_str.replace(" ", "")
                try:
                    dateutil.parser.parse(date_str)
                except ValueError:
                    return None

                return date_str

    def parse_company(self):
        """
        :return: str
            Parses market data
        """

        global market_match
        for int_accuracy in range(10, 6, -1):
            accuracy = int_accuracy / 10.0

            min_accuracy, market_match = -1, None
            for market, spellings in self.config.markets.items():
                for spelling in spellings:
                    line = self.fuzzy_find(spelling, accuracy)
                    if line and (accuracy < min_accuracy or min_accuracy == -1):
                        min_accuracy = accuracy
                        market_match = market
                        return market_match

        return market_match

    def parse_total(self):
        """
        :return: str
            Parses total data
        """

        for sum_key in self.config.sum_keys:
            sum_line = self.fuzzy_find(sum_key)
            if sum_line:
                # Replace all commas with a dot to make
                # finding and parsing the sum easier
                sum_line = sum_line.replace(",", ".")
                # Parse the sum
                sum_float = re.search(self.config.sum_format, sum_line)
                if sum_float:
                    return sum_float.group(0)

    def parse_payment_method(self):
        for payment_method_key in self.config.payment_method_keys:
            payment_method_line = self.fuzzy_find(payment_method_key)
            print(payment_method_line)
            if payment_method_line:
                return payment_method_key.upper() + " " + add_card_number(payment_method_line)
        return "cash"

    def to_json(self):
        """
        :return: json
            Convert Receipt object to json
        """
        object_data = {
            "company": self.company,
            "date": self.date,
            "total": self.total,
            "lines": self.lines
        }

        return json.dumps(object_data)

