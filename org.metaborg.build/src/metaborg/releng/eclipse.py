from metaborg.util.eclipse import EclipseGen


_eclipseRepo = 'http://eclipse.mirror.triple-it.nl/releases/luna/'
_eclipsePackage = 'epp.package.standard'


_spoofaxRepo = 'http://download.spoofax.org/update/nightly/'
_spoofaxRuntime = ['org.strategoxt.imp.feature.group']
_spoofaxMeta = ['org.strategoxt.imp.meta.feature.group']
_modelwareRuntime = [
  'org.metaborg.modelware.gmf.feature.group',
  'org.metaborg.modelware.gmf.headless.feature.group',
  'org.metaborg.modelware.emf.feature.group'
]
_modelwareMeta = ['org.metaborg.modelware.gmf.meta.feature.group', 'org.metaborg.modelware.emf.meta.feature.group']


_m2eRepos = [
  'http://download.eclipse.org/technology/m2e/milestones/1.6',
  'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-buildhelper/0.15.0/N/0.15.0.201405280027/',
  'http://download.jboss.org/jbosstools/updates/m2e-extensions/m2e-jdt-compiler/',
  'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-tycho/0.9.0/N/LATEST/'
]
_m2eFeatures = [
  'org.eclipse.m2e.feature.feature.group',
  'org.sonatype.m2e.buildhelper.feature.feature.group',
  'org.jboss.tools.m2e.jdt.feature.feature.group',
  'org.sonatype.tycho.m2e.feature.feature.group'
]


def GeneratePlainEclipse(destination, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage, **kwargs):
  EclipseGen(destination = destination, repositories = [eclipseRepo], installUnits = [eclipsePackage], **kwargs)

def GenerateSpoofaxEclipse(destination, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage,
    spoofaxRepo = _spoofaxRepo, installMeta = True, installModelware = True, **kwargs):
  repositories = [eclipseRepo, spoofaxRepo]
  installUnits = [eclipsePackage] + _spoofaxRuntime
  if installMeta:
    installUnits += _spoofaxMeta
  if installModelware:
    installUnits += _modelwareRuntime
    if installMeta:
      installUnits += _modelwareMeta
  EclipseGen(destination = destination, repositories = repositories, installUnits = installUnits, **kwargs)

def GenerateDevSpoofaxEclipse(destination, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage,
    spoofaxRepo = _spoofaxRepo, **kwargs):
  repositories = [eclipseRepo, spoofaxRepo] + _m2eRepos
  installUnits = [eclipsePackage] + _spoofaxRuntime + _spoofaxMeta + _modelwareRuntime + _modelwareMeta + _m2eFeatures
  EclipseGen(destination = destination, repositories = repositories, installUnits = installUnits, **kwargs)
