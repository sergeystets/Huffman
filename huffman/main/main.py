'''
Created on 01.10.2012

@author: sergeystets
'''
#!/usr/bin/env python2.7
# coding: utf-8

import heapq
import struct
import cPickle
from collections import Counter

class TreeNode:
    def __init__(self, freq, char='', left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    def __repr__(self):
        return "({0}, {1})".format(self.char, self.freq)

    def __lt__(self, rhs):
        return self.freq < rhs.freq


def buildFreqTable(path):
    BUFSIZE = 512

    freqs = Counter()

    with open(path, "rb") as f:
        buf = f.read(BUFSIZE)
        while buf:
            freqs.update(buf)
            buf = f.read(BUFSIZE)

    return freqs


def buildHalfmanTree(path):
    queue = [TreeNode(freq=t[1], char=t[0]) for t in buildFreqTable(path).most_common()]
    heapq.heapify(queue)

    root = None

    while queue:
        left_node = heapq.heappop(queue)

        if not queue:
            root = left_node
            break

        right_node = heapq.heappop(queue)

        union_node = TreeNode(freq=left_node.freq + right_node.freq, left=left_node, right=right_node)
        heapq.heappush(queue, union_node)

    return root


def buildCode(codeDict, root, code=''):
    '''if node is None return'''
    if root is None:
        return

    ''' check if we rich the node with some char'''
    if root.char:
        '''if true - set char as value by code as a key'''
        codeDict[root.char] = code

    '''else call buildCode for left and for right child node'''
    buildCode(codeDict, root.left, code + '0')
    buildCode(codeDict, root.right, code + '1')


def code(tree, codeDict, readPath, savePath):
    BUFSIZE = 512
    writeBuf = []

    with open(savePath, 'wb') as ofs:
        tree_dumped = cPickle.dumps(tree, 1)
        tree_dumped_size = len(tree_dumped)
        ofs.write(struct.pack("i", tree_dumped_size))
        ofs.write(str(tree_dumped))

        with open(readPath, 'rb') as ifs:
            write_tmp = []

            readBuf = ifs.read(BUFSIZE)
            while readBuf:
                for char in readBuf:
                    code = codeDict[char]
                    write_tmp.extend(code)

                    if len(write_tmp) > 8:
                        writeBuf.append(chr(int("".join(write_tmp[:8]), 2)))
                        write_tmp = write_tmp[8:]

                    if len(writeBuf) > BUFSIZE:
                        ofs.write("".join(writeBuf))
                        writeBuf = []

                readBuf = ifs.read(BUFSIZE)

            if write_tmp:
                writeBuf.append(chr(int("{0:0<8}".format("".join(write_tmp)), 2)))
                writeBuf.append(struct.pack("c", str((8 - len(write_tmp)))))

            if writeBuf:
                ofs.write("".join(writeBuf))
                writeBuf = []


   
def decode(readPath, savePath):
    return
    

if __name__ == "__main__":
    tree = buildHalfmanTree("file.txt")
    codeDict = {}
    buildCode(codeDict, tree)
    code(tree, codeDict, "file.txt", "file.compressed.txt")
