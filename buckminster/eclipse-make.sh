#! /bin/bash

ECLIPSE_REPO="http://download.eclipse.org/eclipse/updates/4.3"
SPOOFAX_REPO="http://download.spoofax.org/update/unstable/"

function eclipse {

  # 1. os
  # 2. ws
  # 3. arch
  # 4. ini path

  echo "Creating Eclipse installation for $1 $2 $3"

  INSTALL_PATH="spoofax-$1-$3"
  INSTALL_ZIP="spoofax-$1-$3.tar.gz"
  INI_PATH="$INSTALL_PATH/$4"

  # Delete old stuff
  rm -rf $INSTALL_PATH
  rm -rf $INSTALL_ZIP

  # Create eclipse installation
  ./director/director \
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
  sed -i '' -e '/^$/d' $INI_PATH
  perl -pi -e "s/^\r\n//" $INI_PATH
  # TODO: Remove -install argument

  # Add own VM arguments
  echo "-Xms512m" >> $INI_PATH
  echo "-Xmx1024m" >> $INI_PATH
  echo "-Xss16m" >> $INI_PATH
  echo "-XX:MaxPermSize=256m" >> $INI_PATH
  echo "-server" >> $INI_PATH

  # Zip it
  tar -cf $INSTALL_ZIP $INSTALL_PATH
  rm -rf $INSTALL_PATH

}


eclipse "macosx" "cocoa" "x86" "Eclipse.app/Contents/MacOS/eclipse.ini"
eclipse "macosx" "cocoa" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini"

eclipse "win32" "win32" "x86" "eclipse.ini"
eclipse "win32" "win32" "x86_64" "eclipse.ini"

eclipse "linux" "gtk" "x86" "Eclipse.app/Contents/MacOS/eclipse.ini"
eclipse "linux" "gtk" "x86_64" "Eclipse.app/Contents/MacOS/eclipse.ini"
