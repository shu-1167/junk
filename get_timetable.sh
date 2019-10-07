#!/bin/bash

mkdir ~/timetable
cd ~/timetable/
rm *.json

curl -X POST -c cookie.txt -d "username=21*****&pass=******&login_button=ログイン" comp2.ecc.ac.jp/sutinfo/login.php
get=`curl -b cookie.txt comp2.ecc.ac.jp/sutinfo/index.php | grep monster/v1/timetable/find_by_code`
token=${get##*=}
token=${token:0:-1}


cat professors_user.txt | while read line
do
    curl comp2.ecc.ac.jp/monster/v1/timetable/find_by_code?code=${line%$'\r'}\&token=$token > ${line%$'\r'}.json
done
