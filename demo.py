#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__    = 'Mu Yang <emfomy@gmail.com>'
__copyright__ = 'Copyright 2018'

import argparse
import sys

import json
import time

import server

class Demo():
    """The demo object"""

    def __init__(self, file):
        """Default constructor."""
        self.__pardata = {}
        self.__ansdata = {}
        with open(file) as fin:
            for key, item in json.load(fin).items():
                self.__pardata[key] = item['paragraph']
                self.__ansdata[key] = item['answer']

    def pardata(self):
        """Load paragraph data.

        Returns:
            dict: the paragraphs.
                * Key   (str): topic.
                * Value (str): paragraph.
        """

        return self.__pardata

    def ansdata(self):
        """Load data.

        Returns:
            dict: the answers.
                * Key   (str):  topic.
                * Value (list): list of answers.
        """

        return self.__ansdata

    def predict(self, p_str, a_str):
        """Get predicted question.

        Args:
            p_str (str): paragraph.
            a_str (str): answer.

        Returns:
            str: predicted question.
        """
        time.sleep(1)
        q_str = f'GUESS [{a_str[:64]}] {p_str[:256]}'
        return q_str

    def truth(self, p_str, a_str):
        """Get ground-truth question.

        Args:
            p_str (str): paragraph.
            a_str (str): answer.

        Returns:
            str: ground-truth question.
        """
        time.sleep(1)
        q_str2 = f'TRUTH [{a_str[-64:]}] {p_str[-256:]}'
        return q_str2


def main():
    """The main function."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='0.0.0.0')
    parser.add_argument('-P', '--port', default=9000, type=int)
    parser.add_argument('-d', '--data', default='data.json')

    args = parser.parse_args()

    demo = Demo(args.data)

    server.run(demo, args.host, args.port)


if __name__ == '__main__':
    main()
    sys.exit()
