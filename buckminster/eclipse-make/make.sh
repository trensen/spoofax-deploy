#! /bin/bash

#ECLIPSE_REPO="http://download.eclipse.org/eclipse/updates/4.3"
#SPOOFAX_REPO="http://download.spoofax.org/update/unstable/"

PWD=`pwd`
ECLIPSE_REPO="file://$PWD/mirror-eclipse/"
SPOOFAX_REPO="file://$PWD/mirror-spoofax/"

function eclipse {

  # 1. os
  # 2. ws
  # 3. arch
  # 4. ini path
  # 5. JRE path relative to ini file

  echo "Creating Eclipse installation for $1 $2 $3"

  INSTALL_PATH="spoofax-$1-$3"
  INSTALL_NOJAVA_ZIP="spoofax-$1-$3-nojre.zip"
  INSTALL_ZIP="spoofax-$1-$3.zip"
  INI_PATH="$INSTALL_PATH/$4"
  JRE_PATH="$INSTALL_PATH/jre"
  JRE_RELATIVE_TO_INI_PATH="$5"

  # Delete old stuff
  rm -rf $INSTALL_PATH
  rm -rf $INSTALL_NOJAVA_ZIP
  rm -rf $INSTALL_ZIP

  # Create eclipse installation
  ../director/director \
    -repository $ECLIPSE_REPO,$SPOOFAX_REPO \
    -destination $INSTALL_PATH \
    -bundlepool $INSTALL_PATH \
    -profile SDKProfile \
    -profileProperties org.eclipse.update.install.features=true \
    -installIU org.eclipse.sdk.ide \
    -installIU org.strategoxt.imp.feature.group \
    -p2.os $1 \
    -p2.ws $2 \
    -p2.arch $3 \
    -roaming

  # Remove regular VM args
  sed -i '' -e 's|-Xms[0-9]*m||' $INI_PATH
  sed -i '' -e 's|-Xss[0-9]*m||' $INI_PATH
  sed -i '' -e 's|-Xmx[0-9]*m||' $INI_PATH
  sed -i '' -e 's|-XX:MaxPermSize=[0-9]*m||' $INI_PATH
  perl -pi -0 -w -e "s/-install\n.+//g" $INI_PATH
  sed -i '' -e '/^$/d' $INI_PATH
  perl -pi -e "s/^\r\n//" $INI_PATH

  # Add own VM arguments
  echo "-Xms512m" >> $INI_PATH
  echo "-Xmx1024m" >> $INI_PATH
  echo "-Xss16m" >> $INI_PATH
  echo "-XX:MaxPermSize=256m" >> $INI_PATH
  echo "-server" >> $INI_PATH

  # Zip it without JRE
  zip -q -r $INSTALL_NOJAVA_ZIP $INSTALL_PATH


  # Copy JRE into Eclipse directory
  mkdir -p $JRE_PATH
  cp -R "jre/$1_$3/." $JRE_PATH

  # Prepend VM argument
  sed -i '' -e "1s;^;-vm@$JRE_RELATIVE_TO_INI_PATH@;" $INI_PATH
  tr "@" "\n" < $INI_PATH > "$INI_PATH.tmp"
  rm $INI_PATH
  mv "$INI_PATH.tmp" $INI_PATH

  # Zip it with JRE
  zip -q -r $INSTALL_ZIP $INSTALL_PATH

  # Delete installation folder
  rm -rf $INSTALL_PATH

}

eclipse "macosx" "cocoa" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini" "../../../jre/bin/java"
eclipse "win32" "win32" "x86" "eclipse.ini" "jre\\\bin\\\javaw.exe"
eclipse "win32" "win32" "x86_64" "eclipse.ini" "jre\\\bin\\\javaw.exe"
eclipse "linux" "gtk" "x86" "eclipse.ini" "jre/bin/java"
eclipse "linux" "gtk" "x86_64" "eclipse.ini" "jre/bin/java"
