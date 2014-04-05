#! /bin/bash

# OSX 32
rm -rf spoofax-osx-x86
./director/director \
  -repository http://download.eclipse.org/eclipse/updates/4.3,http://download.spoofax.org/update/unstable/ \
  -destination spoofax-osx-x86 \
  -bundlepool spoofax-osx-x86 \
  -profile SDKProfile \
  -profileProperties org.eclipse.update.install.features=true \
  -installIU org.eclipse.sdk.ide \
  -installIU org.strategoxt.imp.feature.group \
  -p2.os macosx \
  -p2.ws cocoa \
  -p2.arch x86 \
  -roaming \

# remove vm args
sed -i 's|-Xms[0-9]*m||' spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-Xss[0-9]*m||' spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-Xmx[0-9]*m||' spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-XX:MaxPermSize=[0-9]*m||' spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i '/^$/d' spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
perl -pi -e "s/^\r\n//" spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini

# add own default vmwargs
echo "-Xms512m" >> spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-Xmx1024m" >> spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-Xss16m" >> spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-XX:MaxPermSize=256m" >> spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-server" >> spoofax-osx-x86/Eclipse.app/Contents/MacOS/eclipse.ini


# OSX 64
rm -rf spoofax-osx-x86_64
./director/director \
  -repository http://download.eclipse.org/eclipse/updates/4.3,http://download.spoofax.org/update/unstable/ \
  -destination spoofax-osx-x86_64 \
  -bundlepool spoofax-osx-x86_64 \
  -profile SDKProfile \
  -profileProperties org.eclipse.update.install.features=true \
  -installIU org.eclipse.sdk.ide \
  -installIU org.strategoxt.imp.feature.group \
  -p2.os macosx \
  -p2.ws cocoa \
  -p2.arch x86_64 \
  -roaming \

# remove vm args
sed -i 's|-Xms[0-9]*m||' spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-Xss[0-9]*m||' spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-Xmx[0-9]*m||' spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i 's|-XX:MaxPermSize=[0-9]*m||' spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
sed -i '/^$/d' spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
perl -pi -e "s/^\r\n//" spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini

# add own default vmwargs
echo "-Xms512m" >> spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-Xmx1024m" >> spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-Xss16m" >> spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-XX:MaxPermSize=256m" >> spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini
echo "-server" >> spoofax-osx-x86_64/Eclipse.app/Contents/MacOS/eclipse.ini



# Windows 64
rm -rf spoofax-win32-x86_64
./director/director \
  -repository http://download.eclipse.org/eclipse/updates/4.3,http://download.spoofax.org/update/unstable/ \
  -destination spoofax-win32-x86_64 \
  -bundlepool spoofax-win32-x86_64 \
  -profile SDKProfile \
  -profileProperties org.eclipse.update.install.features=true \
  -installIU org.eclipse.sdk.ide \
  -installIU org.strategoxt.imp.feature.group \
  -p2.os win32 \
  -p2.ws win32 \
  -p2.arch x86_64 \
  -roaming \

# remove vm args
sed -i 's|-Xms[0-9]*m||' spoofax-win32-x86_64/eclipse.ini
sed -i 's|-Xss[0-9]*m||' spoofax-win32-x86_64/eclipse.ini
sed -i 's|-Xmx[0-9]*m||' spoofax-win32-x86_64/eclipse.ini
sed -i 's|-XX:MaxPermSize=[0-9]*m||' spoofax-win32-x86_64/eclipse.ini
sed -i '/^$/d' spoofax-win32-x86_64/eclipse.ini
perl -pi -e "s/^\r\n//" spoofax-win32-x86_64/eclipse.ini

# add own default vmwargs
echo "-Xms512m" >> spoofax-win32-x86_64/eclipse.ini
echo "-Xmx1024m" >> spoofax-win32-x86_64/eclipse.ini
echo "-Xss16m" >> spoofax-win32-x86_64/eclipse.ini
echo "-XX:MaxPermSize=256m" >> spoofax-win32-x86_64/eclipse.ini
echo "-server" >> spoofax-win32-x86_64/eclipse.ini


# Windows 32
rm -rf spoofax-win32-x86
./director/director \
  -repository http://download.eclipse.org/eclipse/updates/4.3,http://download.spoofax.org/update/unstable/ \
  -destination spoofax-win32-x86 \
  -bundlepool spoofax-win32-x86 \
  -profile SDKProfile \
  -profileProperties org.eclipse.update.install.features=true \
  -installIU org.eclipse.sdk.ide \
  -installIU org.strategoxt.imp.feature.group \
  -p2.os win32 \
  -p2.ws win32 \
  -p2.arch x86 \
  -roaming \

# remove vm args
sed -i 's|-Xms[0-9]*m||' spoofax-win32-x86/eclipse.ini
sed -i 's|-Xss[0-9]*m||' spoofax-win32-x86/eclipse.ini
sed -i 's|-Xmx[0-9]*m||' spoofax-win32-x86/eclipse.ini
sed -i 's|-XX:MaxPermSize=[0-9]*m||' spoofax-win32-x86/eclipse.ini
sed -i '/^$/d' spoofax-win32-x86/eclipse.ini
perl -pi -e "s/^\r\n//" spoofax-win32-x86/eclipse.ini

# add own default vmwargs
echo "-Xms512m" >> spoofax-win32-x86/eclipse.ini
echo "-Xmx1024m" >> spoofax-win32-x86/eclipse.ini
echo "-Xss16m" >> spoofax-win32-x86/eclipse.ini
echo "-XX:MaxPermSize=256m" >> spoofax-win32-x86/eclipse.ini
echo "-server" >> spoofax-win32-x86/eclipse.ini
