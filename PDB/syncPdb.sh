#!/bin/bash

#Author: Zhenting Gao
#Update: 1/6/2020

cd /data/databases
rsync -rlpt -v -z --delete --port=33444 rsync.rcsb.org::ftp_data/structures/divided/pdb/ ./pdb

#add this script to Cron table is necessary, here is how to do that
#crontab -e
#0 0,12 * * * zhentg /home/zhentg/bin/rsync_pdb_utility.sh
