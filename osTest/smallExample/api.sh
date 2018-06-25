#!/bin/sh
A=`date '+%Y-%m-%d %H:%M:%S'`
python3 /home/smrt0060/ostest/searchAPI.py > /home/smrt0060/ostest/result_$A.txt
