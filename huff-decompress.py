"""\
----------------------------------------------------------------
USE: python huff_decompress.py (options)
OPTIONS:
    -f FILE: .bin file to decode
"""

import heapq
import pickle
import array
import argparse
import sys
import os
import datetime

class CLI:
    def __init__(self):
        self.exit = False
        parser = argparse.ArgumentParser()
        parser.add_argument("infile", help="text file to encode")
        parser.add_argument("-s", "--symbolmodel",
                            help="specify character- or word-based Huffman encoding",
                            choices=["char", "word"])
        args = parser.parse_args()

        if not (args.infile):
            self.exit = True
            print("Must provide an infile")
            self.print_help()
        else:
            self.file = args.infile
            self.model = args.infile.replace('.bin', '') + '-symbol-model.pkl'

    def print_help(self):
        print(__doc__)


class HuffmanDecode:
    def __init__(self, encoded_text, tree):
        self.decoded_file = self.decode(encoded_text, tree)

    def decode(self, encoded_text, tree):
        code_tree = tree
        decoded = []
        for c in encoded_text:
            if c == '0':
                code_tree = code_tree[1]
            else:
                code_tree = code_tree[2]

            if len(code_tree) == 1:
                freq, label = code_tree[0]
                decoded.append(label)
                code_tree = tree

        return ''.join(decoded)


class Index:
    def __init__(self, file, model):
        self.encoded_text = self.open_file(file)
        self.model = self.open_model(model)

    def remove_pad(self, encoded_text):
        pad_i = encoded_text[:8]
        extra_p = int(pad_i, 2)
        encoded_text = encoded_text[8:]
        encoded_text = encoded_text[:-extra_p]

        return encoded_text

    def open_file(self, file):
        codearray = array.array('B')
        encoded_file = ""

        f = open(file, 'rb')
        codearray = f.read()

        for i in codearray:
            byte = "{0:08b}".format(i)
            encoded_file += byte

        return self.remove_pad(encoded_file)

    def open_model(self, model):
        with open(model, 'rb') as file:
            return pickle.load(file)

if __name__ == '__main__':
    config = CLI()

    if config.exit:
        sys.exit()

    start = datetime.datetime.now()
    index = Index(config.file, config.model)
    e = HuffmanDecode(index.encoded_text, index.model)

    with open(config.file.replace(".bin", "") + "-decompressed.txt", 'w') as file:
        file.write(e.decoded_file)
        file.close()

    end = datetime.datetime.now()
    total_t = end - start
    # Compute and print some diagnostic information
    print("Total decompression time (s): %f" % total_t.total_seconds())
