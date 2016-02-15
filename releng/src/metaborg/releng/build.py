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
    bootstrapStratego = False, strategoTest = True, cleanRepo = False, release = False, deploy = False,
    skipTests = False, skipExpensive = False, skipComponents = [], clean = True, profiles = [], qualifier = None,
    copyArtifactsTo = None, localRepo = _defaultLocalRepo, **mavenArgs):
  basedir = repo.working_tree_dir
  if release:
    profiles.append('release')
  if bootstrapStratego:
    buildStratego = True

  if cleanRepo:
    CleanLocalRepo(localRepo)

  profiles.append('!add-metaborg-snapshot-repos')
  profiles.append('!add-spoofax-eclipse-repos')

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
    result = cmd(basedir = basedir, deploy = deploy, release = release, qualifier = qualifier, noSnapshotUpdates = True, clean = clean,
      profiles = list(profiles), buildStratego = buildStratego, bootstrapStratego = bootstrapStratego,
      strategoTest = strategoTest, skipExpensive = skipExpensive, skipTests = skipTests, resumeFrom = resumeFrom, localRepo = localRepo, **mavenArgs)
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

  pomFile = path.join(basedir, 'releng', 'build', 'parent', 'pom.xml')

  Mvn(pomFile = pomFile, phase = phase, **kwargs)
  return BuildResult([])


def BuildPremadeJars(basedir, deploy, release, extraArgs, clean, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy:deploy-file' if deploy else 'install:install-file'

  pomFile = path.join(basedir, 'releng', 'parent', 'pom.xml')

  # Install make-permissive
  makePermissivePath = path.join(basedir, 'jsglr', 'make-permissive', 'jar')
  makePermissivePom = path.join(makePermissivePath, 'pom.xml')
  makePermissiveJar = path.join(makePermissivePath, 'make-permissive.jar')

  repositoryId = "metaborg-nexus"
  if release:
    deployUrl = 'http://artifacts.metaborg.org/content/repositories/releases/'
  else:
    deployUrl = 'http://artifacts.metaborg.org/content/repositories/snapshots/'

  newExtraArgs = ' -DpomFile="{}" -Dfile="{}" -DrepositoryId={} -Durl={}'.format(makePermissivePom, makePermissiveJar, repositoryId, deployUrl)
  if extraArgs:
    extraArgs = extraArgs + newExtraArgs
  else:
    extraArgs = newExtraArgs

  Mvn(pomFile = pomFile, clean = False, phase = phase, extraArgs = extraArgs, **kwargs)


def BuildOrDownloadStrategoXt(basedir, deploy, buildStratego, bootstrapStratego, strategoTest, **kwargs):
  if buildStratego:
    return BuildStrategoXt(basedir = basedir, deploy = deploy, bootstrap = bootstrapStratego, runTests = strategoTest, **kwargs)
  else:
    return DownloadStrategoXt(basedir, **kwargs)

def DownloadStrategoXt(basedir, clean, profiles, skipExpensive, **kwargs):
  # Allow downloading from snapshot repositories when downloading StrategoXT.
  buildProfiles = list(profiles)
  if '!add-metaborg-snapshot-repos' in buildProfiles:
    buildProfiles.remove('!add-metaborg-snapshot-repos')

  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile = pomFile, clean = False, profiles = buildProfiles, phase = 'dependency:resolve', **kwargs)
  return BuildResult([])

def BuildStrategoXt(basedir, deploy, bootstrap, runTests, skipTests, skipExpensive, **kwargs):
  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')
  phase = 'deploy' if deploy else 'install'

  if bootstrap:
    pomFile = path.join(strategoXtDir, 'bootstrap-pom.xml')
  else:
    pomFile = path.join(strategoXtDir, 'build-pom.xml')

  buildKwargs = dict(kwargs)
  if skipExpensive:
    buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-test': True})
  else:
    buildKwargs.update({'strategoxt-skip-test': skipTests or not runTests})

  # Build StrategoXT
  Mvn(pomFile = pomFile, phase = phase, skipTests = skipTests, **buildKwargs)

  # Build StrategoXT parent POM
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-assembly' : True})

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  Mvn(pomFile = parent_pom_file, phase = phase, skipTests = skipTests, **buildKwargs)

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

  pomFile = path.join(basedir, 'releng', 'build', 'java', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

  return BuildResult([
    BuildArtifact('Spoofax sunshine JAR', glob(path.join(basedir, 'spoofax-sunshine/org.metaborg.sunshine2/target/org.metaborg.sunshine2-*.jar'))[0], 'spoofax-sunshine.jar'),
  ])


def BuildLanguagePoms(basedir, deploy, **kwargs):
  phase = 'deploy' if deploy else 'install'

  pomFile = path.join(basedir, 'releng', 'build', 'language', 'parent', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

  return BuildResult([])


def BuildLanguages(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'

  if skipExpensive:
    kwargs.update({'spoofax.skip' : True})

  pomFile = path.join(basedir, 'releng', 'build', 'language', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

  return BuildResult([])


def BuildSPT(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'

  if skipExpensive:
    kwargs.update({'spoofax.skip' : True})

  pomFile = path.join(basedir, 'releng', 'build', 'language', 'spt', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

  return BuildResult([
    BuildArtifact('SPT testrunner JAR', glob(path.join(basedir, 'spt/org.metaborg.meta.lang.spt.testrunner.cmd/target/org.metaborg.meta.lang.spt.testrunner.cmd-*.jar'))[0], 'spoofax-testrunner.jar'),
  ])


def BuildEclipseDeps(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'

  pomFile = path.join(basedir, 'releng', 'build', 'eclipse', 'deps', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

  return BuildResult([])


def BuildEclipse(basedir, qualifier, deploy, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'install'

  pomFile = path.join(basedir, 'releng', 'build', 'eclipse', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

  return BuildResult([
    BuildArtifact('Spoofax Eclipse update site', path.join(basedir, 'spoofax-eclipse/org.metaborg.spoofax.eclipse.updatesite/target/site_assembly.zip'), 'spoofax-eclipse.zip'),
  ])


def BuildSpoofaxLibs(basedir, deploy, qualifier, buildStratego, bootstrapStratego, strategoTest, skipExpensive, **kwargs):
  phase = 'deploy' if deploy else 'verify'

  pomFile = path.join(basedir, 'releng', 'build', 'libs', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

  return BuildResult([
    BuildArtifact('Spoofax libraries JAR', glob(path.join(basedir, 'releng/build/libs/target/build.libs-*.jar'))[0], 'spoofax-libs.jar'),
  ])


'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
_buildDependencies = OrderedDict([
  ('poms'         , []),
  ('jars'         , ['poms']),
  ('strategoxt'   , ['poms', 'jars']),
  ('java'         , ['poms', 'jars', 'strategoxt']),
  ('languagepoms' , ['poms', 'jars', 'strategoxt', 'java']),
  ('languages'    , ['poms', 'jars', 'strategoxt', 'java', 'languagepoms']),
  ('spt'          , ['poms', 'jars', 'strategoxt', 'java', 'languagepoms', 'languages']),
  ('eclipsedeps'  , ['poms', 'jars', 'strategoxt', 'java', 'languagepoms', 'languages']),
  ('eclipse'      , ['poms', 'jars', 'strategoxt', 'java', 'languagepoms', 'languages', 'eclipsedeps']),
  ('spoofax-libs' , ['poms', 'jars', 'strategoxt', 'java']),
])
_buildCommands = {
  'poms'         : BuildPoms,
  'jars'         : BuildPremadeJars,
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
    repositories.append(('add-metaborg-release-repos', 'metaborg-release-repo', metaborgReleases, None, True, False, True))
  if metaborgSnapshots:
    repositories.append(('add-metaborg-snapshot-repos', 'metaborg-snapshot-repo', metaborgSnapshots, None, False, True, True))
  if spoofaxUpdateSite:
    repositories.append(('add-spoofax-eclipse-repos', 'spoofax-eclipse-repo', spoofaxUpdateSite, 'p2', False, False, False))

  mirrors = []
  if centralMirror:
    mirrors.append(('metaborg-central-mirror', centralMirror, 'central'))

  MvnSetingsGen(location = location, repositories = repositories, mirrors = mirrors)

def GenerateIcons(repo, destination_dir, text = ''):
  from metaborg.util.icons import IconGenerator, ensure_directory_exists
  
  basedir = repo.working_tree_dir
  source_dir = '{}/spoofax/graphics/icons'.format(basedir)
  ensure_directory_exists(destination_dir)
  gen = IconGenerator('{}/spoofax/graphics/fonts/kadwa/Kadwa Font Files/Kadwa-Regular.otf'.format(basedir))
  for source_name in ['spoofax']:
    print('Generating icons for {} '.format(source_name))
    destination_name = source_name
    gen.generate_pngs(source_dir, source_name, destination_dir, destination_name, text)
    gen.generate_ico(source_dir, source_name, destination_dir, destination_name, text)
    #gen.generate_icns(source_dir, source_name, destination_dir, destination_name, text)
