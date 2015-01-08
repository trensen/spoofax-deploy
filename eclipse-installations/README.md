# Building Eclipse installations

This directory contains scripts to create complete Eclipse installations with Spoofax pre-installed, for multiple platforms. To create installations, simply run the build script:

```
./build.sh
```

The resulting installations can be found in the `result` directory.

## Options

The Eclipse and Spoofax update site used to generate installations can be changed in the `common.sh` file by changing the `ECLIPSE_UPDATE_SITE` and `SPOOFAX_UPDATE_SITE` variables.

## Including the JRE

A JRE can be included with the installations so that users do not have to install (the correct version of) the JRE. Run the JRE download script:

```
./jre.sh
```

The build script will now also create installations that include the JRE. 

## Mirroring update sites

By default, the build script fetches Eclipse and Spoofax from online update sites. This always fetches the latest version, but can be slow because nothing is cached. The update sites can be mirrored by running the mirror script:

```
./mirror.sh
```

Note that this can take several hours because the Eclipse update site is huge. Subsequent calls to the mirror script will update the local mirror.

After mirroring, the build script will use the local mirror. To use the online version again, delete the `mirror` directory.

## Sources

* Installing Eclipse using the p2 director: <http://help.eclipse.org/luna/topic/org.eclipse.platform.doc.isv/guide/p2_director.html?cp=2_0_20_2>

* Standalone p2 director download: <http://eclipse.mirror.triple-it.nl/tools/buckminster/products/director_latest.zip>

* Downloading JRE's from command line: <https://ivan-site.com/2012/05/download-oracle-java-jre-jdk-using-a-script/>

* Mirroring Eclipse update sites: <https://wiki.eclipse.org/Equinox_p2_Repository_Mirroring>
