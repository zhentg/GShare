#!/bin/bash

#Author: Zhenting Gao
#Update: 1/6/2020

cd /data/databases
rsync -rlpt -v -z --delete --port=33444 rsync.rcsb.org::ftp_data/structures/divided/pdb/ ./pdb
