"""\
----------------------------------------------------------------
USE: python huff_compress.py (options)
OPTIONS:
    -s LABEL INFILE: generate characterwise or wordwise string (LABEL in (char, word)) and file to encode
"""

import heapq
import sys
import argparse
import re
import pickle
import array
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

        if not (args.symbolmodel):
            self.exit = True
            print("Must provide symbol model")
            self.print_help()
        else:
            self.weighting = args.symbolmodel

        if not (args.infile):
            self.exit = True
            print("Must provide an infile")
            self.print_help()
        else:
            self.file = args.infile

    def print_help(self):
        print(__doc__)


class HuffmanCode:
    def __init__(self, file, prob, weighting):
        start = datetime.datetime.now()
        self.tree = self.generate_tree(prob)
        self.map = self.generate_code_map(self.tree)
        end = datetime.datetime.now()
        self.symbol_model_t = end - start

        start = datetime.datetime.now()
        self.encoded = self.huffman_encode(file, self.map, weighting)
        end = datetime.datetime.now()
        self.encoding_t = end - start

    def generate_tree(self, index):
        heap = []
        for c in index:
            heapq.heappush(heap, [c])

        while len(heap) > 1:
            child_a = heapq.heappop(heap)
            child_b = heapq.heappop(heap)
            freq_a, label_a = child_a[0]
            freq_b, label_b = child_b[0]
            freq = freq_a + freq_b
            label = label_a + label_b
            node = [(freq, label), child_a, child_b]
            heapq.heappush(heap, node)

        return heap.pop()

    def navigate_tree(self, tree, map, code):
        if len(tree) == 1:
            map[tree[0][1]] = code
        else:
            count, child_a, child_b = tree
            self.navigate_tree(child_a, map, code + "0")
            self.navigate_tree(child_b, map, code + "1")

        return map

    def generate_code_map(self, tree):
        map = {}
        return self.navigate_tree(tree, map, '')

    def huffman_encode(self, file, map, weighting):
        encoded_file = ''

        if weighting == 'char':
            with open(file, 'r', encoding='utf8') as f:
                f = f.read()
                for c in f:
                    encoded_file += map[c]

        if weighting == 'word':
            with open(file, 'r', encoding='utf8') as f:
                reg_az = re.compile(r'([\d\s\W_]|[a-zA-Z]+)')  # Match any digit, whitespace, non-word, and any word A-z
                for line in f:

                    mm = reg_az.finditer(line)
                    for m in mm:
                        encoded_file += map[m.group(1)]

        return encoded_file


class Index:
    def __init__(self, file, weighting):
        self.file = file
        self.freq_dict = {}

        if weighting == 'char':
            with open(file, 'r', encoding='utf8') as f:
                f = f.read()
                for c in f:
                    if c not in self.freq_dict:
                        self.freq_dict[c] = 1
                    else:
                        self.freq_dict[c] += 1

        if weighting == 'word':
            with open(file, 'r', encoding='utf8') as f:
                reg_az = re.compile(r'([\d\s\W_]|[a-zA-Z]+)')  # Match any digit, whitespace, non-word, and any word A-z
                for line in f:

                    mm = reg_az.finditer(line)
                    for m in mm:
                        if m.group(1) not in self.freq_dict:
                            self.freq_dict[m.group(1)] = 1
                        else:
                            self.freq_dict[m.group(1)] += 1

        self.freq_dict = self.generate_zero_order_model(freq_dict=self.freq_dict)

        self.final_dict = []
        for key, value in self.freq_dict.items():
            self.final_dict.append((value, key))


    def generate_zero_order_model(self, freq_dict):
        total_character_occurences = sum(freq_dict.values())

        for key, value in freq_dict.items():
            freq_dict[key] = value / total_character_occurences

        return freq_dict


class FileWriter:
    def __init__(self, encoded_file, tree, file):
        self.file = file
        self.write_encoded_file(encoded_file)
        self.write_code_map(tree)

    def write_encoded_file(self, encoded_file):
        pad = 8 - len(encoded_file) % 8
        for i in range(pad):
            encoded_file += "0"

        pad_i = "{0:08b}".format(pad)
        encoded_file = pad_i + encoded_file

        assert len(encoded_file) % 8 == 0

        encoded_file = [encoded_file[i:i + 8] for i in range(0, len(encoded_file), 8)]  # Split encoded_file into segments of 8
        codearray = array.array('B')
        for c in encoded_file:
            codearray.append(int(c, 2))

        f = open(self.file.replace('.txt', '') + '.bin', 'wb')
        codearray.tofile(f)
        f.close()

    def write_code_map(self, tree):
        f = open(self.file.replace('.txt', '') + "-symbol-model.pkl", 'wb')
        pickle.dump(tree, f)


if __name__ == '__main__':
    config = CLI()

    start = datetime.datetime.now()
    index = Index(config.file, config.weighting)
    end = datetime.datetime.now()
    zero_order_t = end - start

    e = HuffmanCode(config.file, index.final_dict, config.weighting)
    FileWriter(e.encoded, e.tree, config.file)  # Writes binary file and symbol model


    # Compute and print some diagnostic information
    print("Time to compute zero order frequency (s): %f" % zero_order_t.total_seconds())
    print("Time to build symbol model (s): %f" % e.symbol_model_t.total_seconds())
    print("Time to encode file (s): %f" % e.encoding_t.total_seconds())
    print("Size of compressed text file (bytes): %d" % os.path.getsize(config.file.replace('.txt', '') + '.bin'))
    print("Size of symbol models (bytes): %d" % os.path.getsize(config.file.replace('.txt', '') + "-symbol-model.pkl"))
