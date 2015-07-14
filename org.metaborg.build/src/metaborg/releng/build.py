from collections import OrderedDict
from os import path, makedirs
import shutil
from datetime import datetime
import time
from glob import glob

from metaborg.util.git import LatestDate, Branch
from metaborg.util.maven import Mvn, MvnSetingsGen, MvnUserSettingsLocation


class BuildResult:
  def __init__(self, artifacts):
    self.artifacts = artifacts

class BuildArtifact:
  def __init__(self, name, location, target):
    self.name = name
    self.location = location
    self.target = target


_defaultLocalRepo = path.join(path.expanduser('~'), '.m2', 'repository')


def BuildAll(repo, components = ['all'], buildDeps = True, resumeFrom = None, buildStratego = False,
    bootstrapStratego = False, strategoTest = True, cleanRepo = True, release = False, deploy = False,
    skipExpensive = False, skipComponents = [], clean = True, profiles = [], qualifier = None,
    copyArtifactsTo = None, localRepo = _defaultLocalRepo, **mavenArgs):
  basedir = repo.working_tree_dir
  if release:
    profiles.append('release')
    buildStratego = True
    bootstrapStratego = True
    strategoTest = True
    clean = True
  if bootstrapStratego:
    buildStratego = True

  if cleanRepo:
    CleanLocalRepo(localRepo)

  profiles.append('!add-metaborg-repositories')

  if not qualifier:
    qualifier = CreateQualifier(repo)
  print('Using Eclipse qualifier {}.'.format(qualifier))

  if buildDeps:
    buildOrder = GetBuildOrder(components)
  else:
    buildOrder = components

  for component in skipComponents:
    if component in buildOrder:
      buildOrder.remove(component)

  artifacts = []
  print('Building component(s): {}'.format(', '.join(buildOrder)))
  for build in buildOrder:
    print('Building: {}'.format(build))
    cmd = GetBuildCommand(build)
    result = cmd(basedir = basedir, deploy = deploy, qualifier = qualifier, noSnapshotUpdates = True, clean = clean,
      profiles = profiles, buildStratego = buildStratego, bootstrapStratego = bootstrapStratego,
      strategoTest = strategoTest, skipExpensive = skipExpensive, resumeFrom = resumeFrom, localRepo = localRepo, **mavenArgs)
    if result:
      artifacts.extend(result.artifacts)

  if copyArtifactsTo:
    makedirs(copyArtifactsTo)
  for artifact in artifacts:
    if copyArtifactsTo:
      copyLocation = '{}/{}'.format(copyArtifactsTo, artifact.target)
      print('Produced artifact "{}" at {}, copying to {}'.format(artifact.name, artifact.location, copyLocation))
      shutil.copyfile(artifact.location, copyLocation)
    else:
      print('Produced artifact "{}" at {}'.format(artifact.name, artifact.location))

def BuildPoms(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'parentpoms', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)
  return BuildResult([])


def BuildOrDownloadStrategoXt(basedir, deploy, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  if buildStratego:
    return BuildStrategoXt(basedir = basedir, deploy = deploy, bootstrap = bootstrapStratego, runTests = strategoTest, **kwargs)
  else:
    return DownloadStrategoXt(basedir, **kwargs)

def DownloadStrategoXt(basedir, clean, profiles, skipExpensive, **kwargs):
  if '!add-metaborg-repositories' in profiles:
    profiles.remove('!add-metaborg-repositories')
  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile = pomFile, clean = False, profiles = profiles, phase = 'dependency:resolve', **kwargs)
  return BuildResult([])

def BuildStrategoXt(basedir, profiles, deploy, bootstrap, runTests, skipTests, skipExpensive, **kwargs):
  if '!add-metaborg-repositories' in profiles:
    profiles.remove('!add-metaborg-repositories')

  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')
  phase = 'deploy' if deploy else 'install'

  if bootstrap:
    pomFile = path.join(strategoXtDir, 'bootstrap-pom.xml')
  else:
    pomFile = path.join(strategoXtDir, 'build-pom.xml')

  buildKwargs = dict(kwargs)
  if skipExpensive:
    buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-assembly' : True, 'strategoxt-skip-test': True})
  else:
    buildKwargs.update({'strategoxt-skip-test': skipTests or not runTests})

  Mvn(pomFile = pomFile, phase = phase, profiles = profiles, skipTests = skipTests, **buildKwargs)

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-assembly' : True})
  Mvn(pomFile = parent_pom_file, phase = phase, profiles = profiles, skipTests = skipTests, **buildKwargs)

  if bootstrap:
    distribDir = '{}/buildpoms/bootstrap3/target/'.format(strategoXtDir)
  else:
    distribDir = '{}/buildpoms/build/target/'.format(strategoXtDir)
  return BuildResult([
    BuildArtifact('StrategoXT distribution', glob('{}/strategoxt-distrib-*-bin.tar'.format(distribDir))[0], 'strategoxt-distrib.tar'),
    BuildArtifact('StrategoXT JAR', '{}/dist/share/strategoxt/strategoxt/strategoxt.jar'.format(distribDir), 'strategoxt.jar'),
    BuildArtifact('StrategoXT minified JAR', glob('{}/buildpoms/minjar/target/strategoxt-min-jar-*.jar'.format(strategoXtDir))[0], 'strategoxt-min.jar'),
  ])

def BuildJava(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'
  if skipExpensive:
    kwargs.update({'skip-generator' : True})
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'java', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)
  return BuildResult([
    BuildArtifact('Spoofax sunshine JAR', glob(path.join(basedir, 'spoofax-sunshine/org.metaborg.sunshine/target/org.metaborg.sunshine-*-shaded.jar'))[0], 'spoofax-sunshine.jar'),
    BuildArtifact('Spoofax benchmarker JAR', glob(path.join(basedir, 'spoofax-benchmark/org.metaborg.spoofax.benchmark.cmd/target/org.metaborg.spoofax.benchmark.cmd-*.jar'))[0], 'spoofax-benchmark.jar'),
  ])

def BuildLanguagePoms(basedir, deploy, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'parentpoms', 'language', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)
  return BuildResult([])

def BuildLanguages(basedir, deploy, profiles, **kwargs):
  phase = 'deploy' if deploy else 'install'

  bootstrapProfiles = list(profiles)
  if '!add-metaborg-repositories' in bootstrapProfiles:
    bootstrapProfiles.remove('!add-metaborg-repositories')
  bootstrapPomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'languages', 'bootstrap', 'pom.xml')
  Mvn(pomFile = bootstrapPomFile, phase = phase, profiles = bootstrapProfiles, **kwargs)

  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'languages', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, profiles = profiles, **kwargs)

  return BuildResult([])

def BuildSPT(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  if skipExpensive:
    kwargs.update({'skip-language-build' : True})
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'spt', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)
  return BuildResult([
    BuildArtifact('SPT testrunner JAR', glob(path.join(basedir, 'spt/org.metaborg.meta.lang.spt.testrunner.cmd/target/org.metaborg.meta.lang.spt.testrunner.cmd-*.jar'))[0], 'spoofax-testrunner.jar'),
  ])

def BuildEclipseDeps(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'eclipsedeps', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)
  return BuildResult([])

def BuildEclipse(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'
  if skipExpensive:
    kwargs.update({'skip-language-build' : True})
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'eclipse', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)
  return BuildResult([
    BuildArtifact('Spoofax Eclipse update site', path.join(basedir, 'spoofax-eclipse/org.metaborg.spoofax.eclipse.updatesite/target/site_assembly.zip'), 'spoofax-eclipse.zip'),
  ])

def BuildSpoofaxLibs(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build', 'spoofax', 'libs', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)
  return BuildResult([
    BuildArtifact('Spoofax libraries JAR', glob(path.join(basedir, 'spoofax-deploy/org.metaborg.maven.build/spoofax/libs/target/org.metaborg.maven.build.spoofax.libs-*.jar'))[0], 'spoofax-libs.jar'),
  ])

'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
_buildDependencies = OrderedDict([
  ('poms'         , []),
  ('strategoxt'   , ['poms']),
  ('java'         , ['poms', 'strategoxt']),
  ('languagepoms' , ['poms', 'strategoxt', 'java']),
  ('languages'    , ['poms', 'strategoxt', 'java', 'languagepoms']),
  ('spt'          , ['poms', 'strategoxt', 'java', 'languagepoms', 'languages']),
  ('eclipsedeps'  , ['poms', 'strategoxt', 'java', 'languagepoms', 'languages']),
  ('eclipse'      , ['poms', 'strategoxt', 'java', 'languagepoms', 'languages', 'eclipsedeps']),
  ('spoofax-libs' , ['poms', 'strategoxt', 'java']),
])
_buildCommands = {
  'poms'         : BuildPoms,
  'strategoxt'   : BuildOrDownloadStrategoXt,
  'java'         : BuildJava,
  'languagepoms' : BuildLanguagePoms,
  'languages'    : BuildLanguages,
  'spt'          : BuildSPT,
  'eclipsedeps'  : BuildEclipseDeps,
  'eclipse'      : BuildEclipse,
  'spoofax-libs' : BuildSpoofaxLibs,
}

def GetAllBuilds():
  return list(_buildDependencies.keys()) + ['all']

def GetBuildOrder(args):
  if 'all' in args:
    return list(_buildDependencies.keys())

  builds = set()
  for name, deps in _buildDependencies.items():
    if name in args:
      builds.add(name)
      for dep in deps:
        builds.add(dep)
  orderedBuilds = []
  for name in _buildDependencies.keys():
    if name in builds:
      orderedBuilds.append(name)
  return orderedBuilds

def GetBuildCommand(build):
  return _buildCommands[build]


def CreateQualifier(repo, branch = None):
  timestamp = LatestDate(repo)
  if not branch:
    branch = Branch(repo)
  return FormatQualifier(timestamp, branch)

def CreateNowQualifier(repo, branch = None):
  timestamp = datetime.now()
  if not branch:
    branch = Branch(repo)
  return FormatQualifier(timestamp, branch)

_qualifierFormat = '%Y%m%d-%H%M%S'
def FormatQualifier(timestamp, branch):
  return '{}-{}'.format(timestamp.strftime(_qualifierFormat), branch)

_qualifierLocation = '.qualifier'
def RepoChanged(repo, qualifierLocation = _qualifierLocation):
  timestamp = LatestDate(repo)
  branch = Branch(repo)
  changed = False;
  if not path.isfile(qualifierLocation):
    changed = True
  else:
    with open(qualifierLocation, mode = 'r') as qualifierFile:
      storedTimestampStr = qualifierFile.readline().replace('\n', '')
      storedBranch = qualifierFile.readline().replace('\n', '')
      if not storedTimestampStr or not storedBranch:
        raise Exception('Invalid qualifier file {}, please delete this file and retry'.format(qualifierLocation))
      storedTimestamp = datetime.fromtimestamp(int(storedTimestampStr))
      changed = (timestamp > storedTimestamp) or (branch != storedBranch)
  with open(qualifierLocation, mode = 'w') as timestampFile:
    timestampStr = str(int(time.mktime(timestamp.timetuple())))
    timestampFile.write('{}\n{}\n'.format(timestampStr, branch))
  return changed, FormatQualifier(timestamp, branch)


def CleanLocalRepo(localRepo):
  print('Cleaning artifacts from local repository')
  metaborgPath = path.join(localRepo, 'org', 'metaborg')
  print('Deleting {}'.format(metaborgPath))
  shutil.rmtree(metaborgPath, ignore_errors = True)
  cachePath = path.join(localRepo, '.cache', 'tycho')
  print('Deleting {}'.format(cachePath))
  shutil.rmtree(cachePath, ignore_errors = True)


_mvnSettingsLocation = MvnUserSettingsLocation()
_metaborgReleases = 'http://artifacts.metaborg.org/content/repositories/releases/'
_metaborgSnapshots = 'http://artifacts.metaborg.org/content/repositories/snapshots/'
_spoofaxUpdateSite = 'http://download.spoofax.org/update/nightly/'
_centralMirror = 'http://artifacts.metaborg.org/content/repositories/central/'

def GenerateMavenSettings(location = _mvnSettingsLocation, metaborgReleases = _metaborgReleases,
    metaborgSnapshots = _metaborgSnapshots, spoofaxUpdateSite = _spoofaxUpdateSite, centralMirror = _centralMirror):
  repositories = []
  if metaborgReleases:
    repositories.append(('add-metaborg-repositories', 'metaborg-nexus-releases', metaborgReleases, None, True, False, True))
  if metaborgSnapshots:
    repositories.append(('add-metaborg-repositories', 'metaborg-nexus-snapshots', metaborgSnapshots, None, False, True, True))
  if spoofaxUpdateSite:
    repositories.append(('add-metaborg-repositories', 'spoofax-nightly', spoofaxUpdateSite, 'p2', False, False, False))

  mirrors = []
  if centralMirror:
    mirrors.append(('metaborg-nexus-central-mirror', centralMirror, 'central'))

  MvnSetingsGen(location = location, repositories = repositories, mirrors = mirrors)
