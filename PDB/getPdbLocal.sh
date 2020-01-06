#!/bin/bash

#Author: Zhenting Gao
#Last Update: 01/06/2020
#
#This script will read a list of PDBID, and create a soft link to the original PDB files synchronized from PDB website
#
#Command line: ./getPdbLocal.sh pdb.lst
#

#Parameters
#Home directory of PDB
localPdbDir='/data/databases/pdb'
#Check if soft link pdb can be read under Windows

if [ $# != 1 ]
then
    echo "Get 1 pdb file, type 'getPdb.sh \"2f4b\"'"
    echo "Get 2 pdb files, type 'getPdb.sh \"2f4b 1a06\"'"
    echo "Get a list of pdb files, type 'getPdb.sh pdb.lst"
    echo 'pdb.lst format:'
    echo '2f4b'
    echo '1F88'
    exit
fi


if [ ! -r $localPdbDir ]
then
    echo 'The local PDB directory is not accessible, this script can not work!'
    exit
fi


retrieved=0


echo "Creat soft link to PDB files from $localPdbDir"
echo "=================="

#Structure of the local PDB directory
#pdb/40
#pdb140d.ent.gz
#pdb140l.ent.gz

#Create or modify list file
if [ ! -f "$1" ]
then
    echo "$1" | tr " " "\n" | sort | sed -e '/^$/d' > pdb.lst
	list="pdb.lst"
else
	list=$1
fi

dos2unix -q $list
sed -i '/^$/d;/PDBID/d;s/:/\t/' $list #Remove blank line and title line
sed -i 's/:/\t/' $list #Convert ':' to "tab"
count=`wc -l $list | awk '{print $1}'`
i=1
log=getPdb.log
#echo 'Missing PDB files' > $log

#Main
while [ $i -le $count ]
do
    pdbIdLowerCase=`sed -n ''"$i"'p' $list | awk '{print $1}' | tr "A-Z" "a-z"`
    pdbIdMiddle=`echo $pdbIdLowerCase | sed -e 's/\s*//g;s/^.//;s/.$//'`
    #Fetch PDB files if the PDB file does not exist in current directory
    if [ ! -s ${pdbIdLowerCase}.ent.gz ]
    then
        #Fetch local PDB files
        if [ -s ${localPdbDir}/${pdbIdMiddle}/pdb${pdbIdLowerCase}.ent.gz ]
        then
            ln -s ${localPdbDir}/${pdbIdMiddle}/pdb${pdbIdLowerCase}.ent.gz ${pdbIdLowerCase}.ent.gz
        else
            echo "Download ${pdbIdLowerCase} from PDB website"
            wget http://www.rcsb.org/pdb/files/${pdbIdLowerCase}.pdb.gz -O pdb${pdbIdLowerCase}.ent.gz >& pdbDownload.log
            mkdir ${localPdbDir}/${pdbIdMiddle}/ >& pdbErr.log
            mv pdb${pdbIdLowerCase}.ent.gz ${localPdbDir}/${pdbIdMiddle}
            ln -s ${localPdbDir}/${pdbIdMiddle}/pdb${pdbIdLowerCase}.ent.gz ${pdbIdLowerCase}.ent.gz
        fi
        if [ -s ${pdbIdLowerCase}.ent.gz ]
        then
            echo ${pdbIdLowerCase}.ent.gz" retrieved!"
            retrieved=`expr $retrieved + 1`
        else
            echo $pdbIdLowerCase "does not exist."
	        echo $pdbIdLowerCase "does not exist." >> $log
        fi
    else
        echo $pdbIdLowerCase" is skipped because it is already in this directory."
    fi
    i=`expr $i + 1`
done

echo "=================="
echo "$retrieved pdb file(s) downloaded."
#echo "Follow this link, http://www.rcsb.org/pdb/files/3Q0Z.ent.gz, to download the missing pdb files."
