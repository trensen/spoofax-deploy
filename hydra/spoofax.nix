{
  nixpkgs ? ../../nixpkgs
    
, aster            ? { outPath = ../../aster ; revCount = 9999; }
, box              ? { outPath = ../../box ; revCount = 9999; }
, esv              ? { outPath = ../../esv ; revCount = 9999; }
, impPatched       ? { outPath = ../../imp-patched ; revCount = 9999; }
, jsglr            ? { outPath = ../../jsglr ; revCount = 9999; }
, lpgRuntime       ? { outPath = ../../lpg-runtime ; revCount = 9999; }
, mbExec           ? { outPath = ../../mb-exec ; revCount = 9999; }
, mbExecDeps       ? { outPath = ../../mb-exec-deps ; revCount = 9999; }
, mbRep            ? { outPath = ../../mb-rep ; revCount = 9999; }
, modelware        ? { outPath = ../../modelware ; revCount = 9999; }
, nabl             ? { outPath = ../../nabl ; revCount = 9999; }
, rtg              ? { outPath = ../../rtg ; revCount = 9999; }
, runtimeLibraries ? { outPath = ../../runtime-libraries ; revCount = 9999; }
, sdf              ? { outPath = ../../sdf ; revCount = 9999; }
, shrike           ? { outPath = ../../shrike ; revCount = 9999; }
, spoofax          ? { outPath = ../../spoofax ; revCount = 9999; }
, spoofaxDebug     ? { outPath = ../../spoofax-debug ; revCount = 9999; }
, spoofaxDeploy    ? { outPath = ../../spoofax-deploy ; revCount = 9999; }
, spoofaxSunshine  ? { outPath = ../../spoofax-sunshine ; revCount = 9999; }
, spt              ? { outPath = ../../spt ; revCount = 9999; }
, stratego         ? { outPath = ../../stratego ; revCount = 9999; }
, strategoxt       ? { outPath = ../../strategoxt ; revCount = 9999; }
, ts               ? { outPath = ../../ts ; revCount = 9999; }

, strategoxtDistrib ? ../../strategoxt-distrib.tar

, mavenEnv  ? "\"-Xmx512m -Xms512m -Xss16m\""
}:
let
  plus = a : b : ( builtins.add a b );
  sumrev = xs : pkgs.lib.foldl plus 0 xs;
  
  spoofaxRev = toString (sumrev [
    aster.revCount box.revCount esv.revCount impPatched.revCount jsglr.revCount lpgRuntime.revCount
    mbExec.revCount mbExecDeps.revCount mbRep.revCount modelware.revCount nabl.revCount rtg.revCount 
    runtimeLibraries.revCount sdf.revCount shrike.revCount spoofax.revCount spoofaxDebug.revCount
    spoofaxDeploy.revCount spoofaxSunshine.revCount spt.revCount stratego.revCount strategoxt.revCount 
    ts.revCount
  ]);
  
  pkgs = import nixpkgs { config.allowUnfree = true; };
  
  jobs = with pkgs.lib; {
    build = pkgs.stdenv.mkDerivation {
      name = "spoofax-${spoofaxRev}";
      
      buildInputs = with pkgs; [ stdenv git openjdk gnutar gzip bash maven3 wget unzip ant ];
      
      buildCommand = ''
        ensureDir $out
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
      	cp -R ${spt}/. $out/spt
      	cp -R ${stratego}/. $out/stratego
      	cp -R ${strategoxt}/. $out/strategoxt
      	cp -R ${ts}/. $out/ts
      	
      	chmod -R +w .
        
        patchShebangs ./


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
      
      	./spoofax-deploy/org.metaborg.maven.build.strategoxt/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.java/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.eclipse/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.libs/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"
      	./spoofax-deploy/org.metaborg.maven.build.spoofax.sunshine/build.sh -e ${mavenEnv} -a "-Dmaven.repo.local=$out/.m2"

      
      	SPOOFAX_SITE_LOC="$out/spoofax-deploy/org.strategoxt.imp.updatesite/target/site"
      	SPOOFAX_SITE_FILE="$out/spoofax-eclipse-${spoofaxRev}.tar.gz"
        touch "''$SPOOFAX_SITE_LOC/index.html"
        tar cvzf ''$SPOOFAX_SITE_FILE ''$SPOOFAX_SITE_LOC
        
        SPOOFAX_LIBS_JAR="$out/spoofax-libs-${spoofaxRev}.jar"
        cp "$out/spoofax-deploy/org.metaborg.maven.build.spoofax.libs/target/spoofax-libs.jar" ''$SPOOFAX_LIBS_JAR
        
        SUNSHINE_JAR="$out/spoofax-sunshine-${spoofaxRev}.jar"
        cp "$out/spoofax-sunshine/org.spoofax.sunshine/target/org.metaborg.sunshine"*".jar" ''$SUNSHINE_JAR
        
        ensureDir $out/nix-support
        echo "file site ''$SPOOFAX_SITE_LOC" >> $out/nix-support/hydra-build-products
        echo "file tar ''$SPOOFAX_SITE_FILE" >> $out/nix-support/hydra-build-products
        echo "file jar ''$SPOOFAX_LIBS_JAR" >> $out/nix-support/hydra-build-products
        echo "file jar ''$SUNSHINE_JAR" >> $out/nix-support/hydra-build-products
      '';
      __noChroot = true;
    };
  };
in jobs
