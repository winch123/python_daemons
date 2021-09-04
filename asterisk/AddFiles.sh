#!/bin/bash

#echo $1
#sleep 0.5
#chown asterisk $1
#mv $1 /tmp/assd

dirr='/tmp/1'
f_count=`ls -f $dirr | wc -l`
f_count=$((1111-$f_count))
echo $f_count

i=0
while [ $i -lt $f_count ]
do
  touch $dirr/aa$RANDOM
  i=$[$i+1]
done
chmod 664 $dirr/aa*
chown asterisk:apache $dirr/aa*
