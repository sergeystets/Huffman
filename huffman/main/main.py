'''
Created on 01.10.2012

@author: sergeystets
'''
#!/usr/bin/env python2.7
# coding: utf-8

import os
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


# build code using code dictionary
def buildCode(codeDict, root, code=''):
    # if node is None return'#
    if root is None:
        return

    # check if we rich the node with some char
    if root.char:
        # if true - set char as value by code as a key#
        codeDict[root.char] = code

    # else call buildCode for left and for right child node
    buildCode(codeDict, root.left, code + '1')
    buildCode(codeDict, root.right, code + '0')


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
                    
                    while len(write_tmp) >= 8:  # if code length is longer than byte length
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
                

# decode file 
def decode(readPath, savePath):   
    BUFSIZE = 512

    with open(readPath, 'rb') as ifs:
        # get tree size
        tree_size = struct.unpack("i", ifs.read(4))[0]
                
        # restore Huffman tree
        tree = cPickle.loads(ifs.read(tree_size))
               
        # restore information about unnecessary zeroes
        ifs.seek(-1, os.SEEK_END)
        unnecessary_zeros = ord(struct.unpack('c', ifs.read(1))[0])

        # get data size
        end = ifs.tell()
        ifs.seek(4 + tree_size)
        start = ifs.tell()
        data_size = end - start

        # restore data
        with open(savePath, "wb") as ofs:
            processed_bytes = 0
            cur_node = tree
            bits_buf = []
            out_buf = []

            while processed_bytes < data_size:
                cur_byte = ord(ifs.read(1))
                bits_buf.extend(cur_byte & (1 << i) for i in xrange(7, -1, -1))

                if processed_bytes == data_size - 1:  # the last byte
                    bits_buf = bits_buf[-unnecessary_zeros:]

                pos = 0
                for b in bits_buf:
                    pos += 1

                    if b:
                        cur_node = cur_node.left
                    else:
                        cur_node = cur_node.right

                    if cur_node.char:
                        out_buf.append(cur_node.char)
                        cur_node = tree
                bits_buf = bits_buf[pos:]

                if len(out_buf) > BUFSIZE:
                    ofs.write("".join(out_buf))
                    out_buf = []

                processed_bytes += 1

            if out_buf:
                ofs.write("".join(out_buf))
                out_buf = []


# search char in Huffman tree by given path
def findChar(root, path):
    if root is None:
        return None
    
    if root.char:
        return root.char
    
    if not path:
        return 
   
    if path[0] == '1':
        return findChar(root.left, path[1:])
    else:
        return  findChar(root.right, path[1:])
    
            
# main method
if __name__ == "__main__":
    print "build tree...."
    tree = buildHalfmanTree("file.txt")
    print "done"
    codeDict = {}
    print "build code...."
    buildCode(codeDict, tree)
    print "done "
    print "coding file....."
    code(tree, codeDict, "file.txt", "file.compressed.txt")
    print "done"
    print "decoding file...."
    decode("file.compressed.txt", "file.decompressed.txt")
    print "done"

