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

# Class TreeNode represents a node for a Huffman tree
class TreeNode:
    def __init__(self, freq, char='', left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

    # is used by print() for printing object into console 
    def __repr__(self):
        return "({0}, {1})".format(self.char, self.freq)

    # is used for objects comparison
    def __lt__(self, rhs):
        return self.freq < rhs.freq

''' 
build hash table (k.v) or dictionary (k -character,
 v - character frequency) from file given in a path parameter
 '''
def buildFreqTable(path):
    BUFSIZE = 512
    
    freqs = Counter()  # dictionary

    # read from file and write to dictionary
    with open(path, "rb") as f:
        buf = f.read(BUFSIZE)
        while buf:
            freqs.update(buf)
            buf = f.read(BUFSIZE)

    return freqs

# build Huffman tree from file given in path parameter
def buildHalfmanTree(path):
    # build descending ordered queue of tree nodes
    queue = [TreeNode(freq=t[1], char=t[0]) for t in buildFreqTable(path).most_common()]
    # and push it to heap
    heapq.heapify(queue)

    root = None

    while queue:
        # get  the smallest element from heap and set to left child
        left_node = heapq.heappop(queue)

        if not queue:  # tree is build
            root = left_node
            break

        # get the smallest element from heap and set to right child
        right_node = heapq.heappop(queue)
        # unite left and right child frequencies and create new node
        union_node = TreeNode(freq=left_node.freq + right_node.freq, left=left_node, right=right_node)
        # push it to heap along with the queue
        heapq.heappush(queue, union_node)

    return root


def buildCode(codeDict, root, code=''):
    # if node is None return'#
    if root is None:
        return

    # check if we rich the node with some char
    if root.char:
        # if true - set char as value by code as a key#
        codeDict[root.char] = code

    # else call buildCode for left and for right child node
    buildCode(codeDict, root.left, code + '0')
    buildCode(codeDict, root.right, code + '1')

# code file using Huffman algorithm
def code(tree, codeDict, readPath, savePath):
    BUFSIZE = 512
    writeBuf = []

    with open(savePath, 'wb') as ofs:
        # serialization of tree
        tree_dumped = cPickle.dumps(tree, 1)
        tree_dumped_size = len(tree_dumped)
        ofs.write(struct.pack("i", tree_dumped_size))
        ofs.write(str(tree_dumped))

        # open file for writing
        with open(readPath, 'rb') as ifs:
            write_tmp = []

            readBuf = ifs.read(BUFSIZE)
            while readBuf:
                for char in readBuf:
                    code = codeDict[char]  # get code for char
                    write_tmp.extend(code)  # save it

                    if len(write_tmp) > 8:  # if code length is longer than byte length
                        writeBuf.append(chr(int("".join(write_tmp[:8]), 2)))  # convert 8 'bits' of code to byte 
                        write_tmp = write_tmp[8:]  # and save the remaining 'bits'

                    if len(writeBuf) > BUFSIZE:  # if write buffer is full 
                        ofs.write("".join(writeBuf))  # write it to file
                        writeBuf = []  # clear write buffer

                readBuf = ifs.read(BUFSIZE)  # read another part of the file

            # last loop
            if write_tmp:  # if there are still some 'bits'
                # add it to write buffer appending 0s
                writeBuf.append(chr(int("{0:0<8}".format("".join(write_tmp)), 2)))
                # add information of how many 0s have been added
                writeBuf.append(struct.pack("c", str((8 - len(write_tmp)))))  

            # write to file
            if writeBuf:
                ofs.write("".join(writeBuf))
                writeBuf = []


#decode file 
def decode(readPath, savePath):
    return
    

if __name__ == "__main__":
    tree = buildHalfmanTree("file.txt")
    codeDict = {}
    buildCode(codeDict, tree)
    code(tree, codeDict, "file.txt", "file.compressed.txt")
=======
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
>>>>>>> branch 'master' of https://github.com/sergeystets/GitRepo.git
