#! /bin/bash

JAR='jar'

rm -rf jartmp
mkdir -p jartmp
cd jartmp

find ../out -name *.jar ! -name *junit* -print0 | while read -d $'\0' file
do
	echo "Unjarring $file"
	cat $file | $JAR x
done

rm -rf 'META-INF'

cd ..
echo 'Jarring spoofax-libs.jar'
$JAR cf spoofax-libs.jar jartmp

rm -rf jartmp