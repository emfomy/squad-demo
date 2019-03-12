#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__    = 'Mu Yang <emfomy@gmail.com>'
__copyright__ = 'Copyright 2019'

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
        self.__qadata  = {}
        with open(file) as fin:
            for data in json.load(fin)['data']:
                title = data['title']
                for i, item in enumerate(data['paragraphs']):
                    key = f'{title}#{i}'
                    self.__pardata[key] = item['context']
                    self.__qadata[key] = []
                    for subitem in item['qas']:
                        if len(subitem['answers']) > 0:
                            self.__qadata[key].append((subitem['question'], subitem['answers'][0]['text'],))

    def pardata(self):
        """Load paragraph data.

        Returns:
            dict: the paragraphs.
                * Key   (str): topic.
                * Value (str): paragraph.
        """

        return self.__pardata

    def qadata(self):
        """Load data.

        Returns:
            dict: the questions and answers.
                * Key   (str):  topic.
                * Value (list): list of (question, answer)s.
        """

        return self.__qadata

    def predict(self, p_str, q_str):
        """Get predicted answer.

        Args:
            p_str (str): paragraph.
            q_str (str): questions.

        Returns:
            str: predicted answer.
        """
        time.sleep(1)
        return q_str.split('Q: ')[-1]


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
