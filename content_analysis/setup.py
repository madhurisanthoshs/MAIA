# to avoid putting this code in every file, instead just importing it 
import sys
import os
cur = os.path.dirname(os.path.abspath(__file__))
par = os.path.abspath(os.path.join(cur, '..'))
sys.path.insert(0, par)