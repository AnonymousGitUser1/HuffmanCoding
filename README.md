# HuffmanCoding

Description
=============================================================

Sample python project for lossless data compression of
text files using Huffman coding algorithm.

https://en.wikipedia.org/wiki/Huffman_coding

Installation Notes
=============================================================

Repository contains two files:

<b>huff_compress.py:</b> Utility for compressing text files
<b>huff_compress.py:</b> Utility for decompressing text files

Files can be run from command line. 
Python should be installed.

huff_compress.py
=============================================================

OPTIONS:
-s LABEL INFILE: generate characterwise or wordwise string 
(LABEL in (char, word)) and file to encode

huff_decompress.py
=============================================================

OPTIONS:
    -f FILE: .bin file to decode (file should have been
    compressed with huff_compress.py)
