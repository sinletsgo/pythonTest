#!/bin/sh
A=`date '+%Y-%m-%d %H:%M:%S'`
python3 /home/kopoprof/smallExample/searchApi.py > /home/kopoprof/smallExample/result_$A.txt 
