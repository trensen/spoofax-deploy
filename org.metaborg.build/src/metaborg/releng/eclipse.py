from metaborg.util.eclipse import EclipseGen, EclipseIniFix, CurrentEclipseOS


_eclipseRepo = 'http://eclipse.mirror.triple-it.nl/releases/luna/'
_eclipsePackage = 'epp.package.standard'


_spoofaxRepo = 'http://download.spoofax.org/update/nightly/'
_spoofaxRuntime = ['org.metaborg.spoofax.eclipse.feature.feature.group']
_spoofaxMeta = ['org.metaborg.spoofax.eclipse.meta.feature.feature.group']
_spoofaxUpdateLocation = 'spoofax-eclipse/org.metaborg.spoofax.eclipse.updatesite/target/site'
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


def GeneratePlainEclipse(destination, eclipseOS = None, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage, repositories = [], installUnits = [], **kwargs):
  if not eclipseOS:
    eclipseOS = CurrentEclipseOS()

  repositories.append(eclipseRepo)
  installUnits.append(eclipsePackage)

  EclipseGen(destination = destination, eclipseOS = eclipseOS, repositories = repositories, installUnits = installUnits, **kwargs)
  EclipseIniFix(destination = destination, eclipseOS = eclipseOS, requiredJavaVersion = None)

def GenerateSpoofaxEclipse(destination, eclipseOS = None, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage,
    spoofaxRepo = _spoofaxRepo, repositories = [], installUnits = [], installMeta = True, installModelware = True, **kwargs):
  if not eclipseOS:
    eclipseOS = CurrentEclipseOS()

  repositories.extend([eclipseRepo, spoofaxRepo]);
  installUnits.extend([eclipsePackage] + _spoofaxRuntime)
  if installMeta:
    installUnits.extend(_spoofaxMeta)
  if installModelware:
    installUnits.extend(_modelwareRuntime)
    if installMeta:
      installUnits.extend(_modelwareMeta)

  EclipseGen(destination = destination, eclipseOS = eclipseOS, repositories = repositories, installUnits = installUnits, **kwargs)
  EclipseIniFix(destination = destination, eclipseOS = eclipseOS)

def GenerateDevSpoofaxEclipse(destination, eclipseOS = None, eclipseRepo = _eclipseRepo, eclipsePackage = _eclipsePackage,
    spoofaxRepo = _spoofaxRepo, repositories = [], installUnits = [], **kwargs):
  if not eclipseOS:
    eclipseOS = CurrentEclipseOS()

  repositories.extend([eclipseRepo, spoofaxRepo] + _m2eRepos)
  installUnits.extend([eclipsePackage] + _spoofaxRuntime + _spoofaxMeta + _modelwareRuntime + _modelwareMeta + _m2eFeatures)

  EclipseGen(destination = destination, eclipseOS = eclipseOS, repositories = repositories, installUnits = installUnits, **kwargs)
  EclipseIniFix(destination = destination, eclipseOS = eclipseOS)
