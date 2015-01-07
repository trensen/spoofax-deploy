#!/usr/bin/env bash


# Error early
set -eu


# Set common arguments
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

DIRECTOR_LOCATION="$DIR/director"
ECLIPSE_LOCATION="$DIR/eclipse"
MIRROR_LOCATION="$DIR/mirror"
JRE_LOCATION="$DIR/jre"
RESULT_LOCATION="$DIR/result"

ECLIPSE_UPDATE_SITE="http://download.eclipse.org/releases/luna/"
ECLIPSE_UPDATE_MIRROR="$MIRROR_LOCATION/eclipse"
SPOOFAX_UPDATE_SITE="http://download.spoofax.org/update/stable/"
SPOOFAX_UPDATE_MIRROR="$MIRROR_LOCATION/spoofax"


# Set Eclipse and Spoofax repositories
if [ -d "$ECLIPSE_UPDATE_MIRROR" ]; then
  ECLIPSE_REPO="file://$ECLIPSE_UPDATE_MIRROR";
  echo "Using mirrored Eclipse repository: $ECLIPSE_REPO";
else
  ECLIPSE_REPO="$ECLIPSE_UPDATE_SITE";
  echo "Using online Eclipse repository: $ECLIPSE_REPO";
fi

if [ -d "$SPOOFAX_UPDATE_MIRROR" ]; then
  SPOOFAX_REPO="file://$SPOOFAX_UPDATE_MIRROR";
  echo "Using mirrored Spoofax repository: $SPOOFAX_REPO";
else
  SPOOFAX_REPO="$SPOOFAX_UPDATE_SITE";
  echo "Using online Spoofax repository: $SPOOFAX_REPO";
fi


function install-director {
	if [ ! -d "$DIRECTOR_LOCATION" ]; then
		echo "Installing director..."

		rm -rf "$DIRECTOR_LOCATION"
		rm -f director.zip
		wget -q -O director.zip http://eclipse.mirror.triple-it.nl/tools/buckminster/products/director_latest.zip
		unzip -q director.zip
		rm director.zip
	fi
}

function eclipse {
	# 1. os
	# 2. ws
	# 3. arch
	# 4. destination
	# 5. extra arguments

	mkdir -p $4
	"$DIRECTOR_LOCATION/director" \
		-installIU epp.package.standard \
		-destination $4 \
		-bundlepool $4 \
		-tag InitialState \
		-profile SDKProfile \
		-profileProperties org.eclipse.update.install.features=true \
		-p2.os $1 \
		-p2.ws $2 \
		-p2.arch $3 \
		-roaming \
		$5
}

function install-default-eclipse {
	if [ ! -d "$ECLIPSE_LOCATION" ]; then
		echo "Installing default eclipse..."
 
		eclipse "macosx" "cocoa" "x86_64" "eclipse" "-repository $ECLIPSE_UPDATE_SITE"
	fi
}

function mirror {
	# 1. source
	# 2. destination

	mkdir -p $2
	"$ECLIPSE_LOCATION/eclipse" \
		-nosplash \
		-verbose \
		-application org.eclipse.equinox.p2.artifact.repository.mirrorApplication \
	 	-source $1 \
	 	-destination $2
}

function spoofax {
	# 1. os
	# 2. ws
	# 3. arch
	# 4. ini path
	# 5. JRE path relative to ini file

	echo "Creating Spoofax installation for $1 $2 $3";

	INSTALL_ARGS="-repository $ECLIPSE_REPO,$SPOOFAX_REPO -installIU org.strategoxt.imp.feature.group,org.spoofax.modelware.gmf.feature.feature.group,org.spoofax.modelware.emf.feature.feature.group"
	INSTALL_PATH="$RESULT_LOCATION/spoofax-$1-$3"
	INSTALL_NOJAVA_ZIP="$RESULT_LOCATION/spoofax-$1-$3-nojre.zip"
	INSTALL_ZIP="$RESULT_LOCATION/spoofax-$1-$3.zip"
	INI_PATH="$INSTALL_PATH/$4"

	# Create Eclipse installation
	rm -rf $INSTALL_PATH
	rm -f $INSTALL_NOJAVA_ZIP
	rm -f $INSTALL_ZIP
	eclipse $1 $2 $3 $INSTALL_PATH "$INSTALL_ARGS"

	# Remove regular VM args
	sed -i '' -e 's|-Xms[0-9]*m||' $INI_PATH;
	sed -i '' -e 's|-Xss[0-9]*m||' $INI_PATH;
	sed -i '' -e 's|-Xmx[0-9]*m||' $INI_PATH;
	sed -i '' -e 's|-XX:MaxPermSize=[0-9]*m||' $INI_PATH;
	sed -i '' -e 's|-Dorg\.eclipse\.swt\.internal\.carbon\.smallFonts||' $INI_PATH;
	perl -pi -0 -w -e "s/-install\n.+//g" $INI_PATH;
	sed -i '' -e '/^$/d' $INI_PATH;
	perl -pi -e "s/^\r\n//" $INI_PATH;

	# Add own VM arguments
	echo "-Xms512m" >> $INI_PATH;
	echo "-Xmx1024m" >> $INI_PATH;
	echo "-Xss16m" >> $INI_PATH;
	echo "-XX:MaxPermSize=256m" >> $INI_PATH;
	echo "-server" >> $INI_PATH;

	# Create an archive without JRE
	echo "Archiving without JRE included: $INSTALL_NOJAVA_ZIP";
	zip -q -r $INSTALL_NOJAVA_ZIP $INSTALL_PATH;

	# Create an archive with JRE
	JRE_PATH="$JRE_LOCATION/$1-$3" 
	if [ ! -d "$JRE_PATH" ]; then
		echo "JRE for $1 $3 does not exist, please download and unpack this JRE into $JRE_PATH, skipping..."
	else
	    echo "Including JRE from $JRE_PATH";

	    JRE_TARGET_PATH="$INSTALL_PATH/jre";
	    
	    # Copy JRE into Eclipse directory
	    mkdir -p $JRE_TARGET_PATH;
	    cp -R "$JRE_PATH/." $JRE_TARGET_PATH;

	    # Prepend VM argument
	    sed -i '' -e "1s;^;-vm@$5@;" $INI_PATH;
	    tr "@" "\n" < $INI_PATH > "$INI_PATH.tmp";
	    rm $INI_PATH;
	    mv "$INI_PATH.tmp" $INI_PATH;

	    # Zip it with JRE
	    echo "Archiving with JRE included: $INSTALL_ZIP";
	    zip -q -r $INSTALL_ZIP $INSTALL_PATH;
	fi
}

# Ensure that the director and default eclipse are installed
install-director
install-default-eclipse
