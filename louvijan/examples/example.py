# coding=utf-8
"""example.py - This file is used as an example.
"""
import louvijan
from louvijan import PipeLine
from louvijan import Config

#  Output configuration template
# Config().template()

# Execute in serial
PipeLine(
    'a.py', 'b.py', 'c.py'
)()
#
# # Execute in parallel
PipeLine(
    ['a.py', 'b.py', 'c.py']
)()

# Serial and parallel execution
PipeLine(
    'a.py', ['b.py', 'c.py'], 'a.py'
)()

# Multiple nesting PipeLine item
#       -> b
# a ->  -> c            -> a
#       -> a -> a -> a
PipeLine(
    'a.py', PipeLine(['b.py', 'c.py', PipeLine('a.py', 'a.py', 'a.py')]), 'a.py'
)()

# # Specify the configuration file
PipeLine(
    'a.py', 'b.py', 'c.py', 'b.py', config='example.conf'
)()

# Specify the configuration file for the specified PipeLine items
PipeLine(
    'a.py', 'b.py', PipeLine('c.py', 'b.py', config='example.conf'),
    PipeLine('a.py', 'b.py', config='example_.conf')
)()