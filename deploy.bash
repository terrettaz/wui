#!/usr/bin/env bash

set -e

WORK=/tmp

dir="$WORK/$RANDOM"
while [ -a $dir ]
do
    dir="$WORK/$RANDOM"
done

echo "creating tmp dir .. "
mkdir -p $dir/wui

echo "copying files .. "
cp -r . $dir/wui

echo "cleaning dev files .. "
rm -rf $dir/wui/deploy.bash \
       $dir/wui/src/site/wui/public\.htaccess \
       $dir/wui/src/site/wui/public\media

find $dir/wui -name '.git' -print | xargs rm -rf

echo "creating archive .. "
version=$RANDOM
tar jcf "wui-$version.tbz2" -C $dir wui

echo "uploading to pluton .. "
scp  wui-$version.tbz2 pluton:

echo "cleaning files .. "
rm -rf wui-$version.tbz2 \
       $dir
echo "done"