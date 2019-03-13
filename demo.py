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

    def __init__(self, file, resfile):
        """Default constructor."""
        self.__pardata = {}
        self.__qadata  = {}
        with open(file) as fin:
            for data in json.load(fin)['data']:
                title = data['title']
                for i, item in enumerate(data['paragraphs']):
                    key = f'{title}#{i+1:02}'
                    self.__pardata[key] = item['context']
                    self.__qadata[key] = []
                    for subitem in item['qas']:
                        anslist = [ans['text'] for ans in subitem['answers']]
                        self.__qadata[key].append((subitem['question'], anslist, subitem['id'],))

        self.__resdata = {}
        with open(resfile) as fin:
            for idx, text in json.load(fin).items():
                self.__resdata[idx] = text

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

    def predict(self, p_str, q_str, idx):
        """Get predicted answer.

        Args:
            p_str (str): paragraph.
            q_str (str): questions.

        Returns:
            str: predicted answer.
        """
        # time.sleep(1)
        # return q_str.split('Q: ')[-1]
        return self.__resdata[idx]


def main():
    """The main function."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='0.0.0.0')
    parser.add_argument('-P', '--port', default=9000, type=int)
    parser.add_argument('-d', '--data', default='data.json')
    parser.add_argument('-r', '--res',  default='res.json')

    args = parser.parse_args()
    print(args)

    demo = Demo(args.data, args.res)

    server.run(demo, args.host, args.port)


if __name__ == '__main__':
    main()
    sys.exit()
