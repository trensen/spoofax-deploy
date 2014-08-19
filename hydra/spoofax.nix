{
  nixpkgs ? ../../nixpkgs
    
, aster            ? { outPath = ../../aster }
, box              ? { outPath = ../../box }
, esv              ? { outPath = ../../esv }
, impPatched       ? { outPath = ../../imp-patched }
, jsglr            ? { outPath = ../../jsglr }
, lpgRuntime       ? { outPath = ../../lpg-runtime }
, mbExec           ? { outPath = ../../mb-exec }
, mbExecDeps       ? { outPath = ../../mb-exec-deps }
, mbRep            ? { outPath = ../../mb-rep }
, modelware        ? { outPath = ../../modelware }
, nabl             ? { outPath = ../../nabl }
, rtg              ? { outPath = ../../rtg }
, runtimeLibraries ? { outPath = ../../runtime-libraries }
, sdf              ? { outPath = ../../sdf }
, shrike           ? { outPath = ../../shrike }
, spoofax          ? { outPath = ../../spoofax }
, spoofaxDebug     ? { outPath = ../../spoofax-debug }
, spoofaxDeploy    ? { outPath = ../../spoofax-deploy }
, spoofaxSunshine  ? { outPath = ../../spoofax-sunshine }
, spoofaxReleng    ? { outPath = ../../spoofax-releng }
, spt              ? { outPath = ../../spt }
, stratego         ? { outPath = ../../stratego }
, strategoxt       ? { outPath = ../../strategoxt }
, ts               ? { outPath = ../../ts }

, strategoxtDistrib ? ../../strategoxt-distrib.tar

, mavenEnv  ? "\"-Xmx512m -Xms512m -Xss16m\""
}:
let
  pkgs = import nixpkgs { config.allowUnfree = true; };
  
  jobs = with pkgs.lib; {
    build = pkgs.stdenv.mkDerivation {
      name = "spoofax";
      
      buildInputs = with pkgs; [ stdenv git openjdk gnutar gzip bash maven3 wget unzip ant ];
      
      buildCommand = ''
        # Copy source code to build environment, and set write permissions.
        mkdir -p $out
        cd $out
        
      	cp -R ${aster}/. $out/aster
      	cp -R ${box}/. $out/box
      	cp -R ${esv}/. $out/esv
      	cp -R ${impPatched}/. $out/imp-patched
      	cp -R ${jsglr}/. $out/jsglr
      	cp -R ${lpgRuntime}/. $out/lpg-runtime
      	cp -R ${mbExec}/. $out/mb-exec
      	cp -R ${mbExecDeps}/. $out/mb-exec-deps
      	cp -R ${mbRep}/. $out/mb-rep
      	cp -R ${modelware}/. $out/modelware
      	cp -R ${nabl}/. $out/nabl
      	cp -R ${rtg}/. $out/rtg
      	cp -R ${runtimeLibraries}/. $out/runtime-libraries
      	cp -R ${sdf}/. $out/sdf
      	cp -R ${shrike}/. $out/shrike
      	cp -R ${spoofax}/. $out/spoofax
      	cp -R ${spoofaxDebug}/. $out/spoofax-debug
      	cp -R ${spoofaxDeploy}/. $out/spoofax-deploy
      	cp -R ${spoofaxSunshine}/. $out/spoofax-sunshine
      	cp ${spoofaxReleng}/latest-timestamp.sh $out/latest-timestamp.sh
      	cp -R ${spt}/. $out/spt
      	cp -R ${stratego}/. $out/stratego
      	cp -R ${strategoxt}/. $out/strategoxt
      	cp -R ${ts}/. $out/ts
      	
      	chmod -R +w .


        # Patch shebangs in scripts to work with nix.        
        patchShebangs ./


        # Build everything
      	cd spoofax-deploy/org.metaborg.maven.build.strategoxt
      	mkdir strategoxt-distrib
      	cd strategoxt-distrib
        if [[ -d ${strategoxtDistrib} ]]; then
          tar -xf ${strategoxtDistrib}/strategoxt-distrib.tar
        else
          tar -xf ${strategoxtDistrib}
        fi
      	chmod a+x share/strategoxt/macosx/*
      	chmod a+x share/strategoxt/linux/*
      	cd $out
      
        QUALIFIER=$(./latest-timestamp.sh)
      
      	./spoofax-deploy/org.metaborg.maven.build.strategoxt/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.java/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2" -q $QUALIFIER
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.eclipse/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2" -q $QUALIFIER
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.libs/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.sunshine/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"


        # Set hydra build products.
      	SPOOFAX_SITE_LOC="$out/spoofax-deploy/org.strategoxt.imp.updatesite/target"
      	SPOOFAX_SITE_FILE="$out/spoofax-eclipse-$QUALIFIER.tar.gz"
        touch "$SPOOFAX_SITE_LOC/index.html"
        tar -C $SPOOFAX_SITE_LOC -cvzf $SPOOFAX_SITE_FILE site
        
        SPOOFAX_LIBS_JAR="$out/spoofax-libs-$QUALIFIER.jar"
        cp "$out/spoofax-deploy/org.metaborg.maven.build.spoofax.libs/target/org.metaborg.maven.build.spoofax.libs"*".jar" $SPOOFAX_LIBS_JAR
        
        SUNSHINE_JAR="$out/spoofax-sunshine-$QUALIFIER.jar"
        cp "$out/spoofax-sunshine/org.spoofax.sunshine/target/org.metaborg.sunshine"*".jar" $SUNSHINE_JAR
        
        mkdir -p $out/nix-support
        echo "file site $SPOOFAX_SITE_LOC" >> $out/nix-support/hydra-build-products
        echo "file tar $SPOOFAX_SITE_FILE" >> $out/nix-support/hydra-build-products
        echo "file jar $SPOOFAX_LIBS_JAR" >> $out/nix-support/hydra-build-products
        echo "file jar $SUNSHINE_JAR" >> $out/nix-support/hydra-build-products
      '';
      
      
      # Allow access to the internet for Maven.
      __noChroot = true;
    };
  };
in jobs
