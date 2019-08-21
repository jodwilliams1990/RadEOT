import matplotlib.pyplot as plt
import ast
import argparse
from argparse import ArgumentDefaultsHelpFormatter as Formatter

description = ('Plot a graph of x against y to show the relationship between them')
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-f', '--files', dest='input_paths', nargs='+', required=True, help='')
parser.add_argument('-x', '--xaxis', dest='x', nargs='+', required=True, help='')
parser.add_argument('-y', '--yaxis', dest='y', nargs='+', required=True, help='')
args = parser.parse_args()
y=''.join(args.y)
x=''.join(args.x)
inputpath=''.join(args.input_paths)

plt.figure()
plt.subplot(111)
g = open(inputpath,"r")
for row in g:
    rt = str(row)
    ns=ast.literal_eval(rt) #print(row)
    plt.scatter(ns[x], ns[y], color='b')#plt.plot([1,2,3,4])
    plt.xlabel(x)
    plt.ylabel(y)
plt.show()
g.close()