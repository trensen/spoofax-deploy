from collections import OrderedDict
from os import path
import shutil

from metaborg.util.git import LatestDate
from metaborg.util.maven import Mvn


def DownloadStrategoXt(basedir):
  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile = pomFile, clean = False, phase = 'dependency:resolve')

def BuildStrategoXt(basedir, deploy, runTests, **kwargs):
  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')
  phase = 'deploy' if deploy else 'install'

  pomFile = path.join(strategoXtDir, 'build-pom.xml')
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-test': not runTests})
  Mvn(pomFile = pomFile, phase = phase, **buildKwargs)

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  buildKwargs = dict(kwargs)
  buildKwargs.update({'strategoxt-skip-build': True, 'strategoxt-skip-assembly' : True})
  Mvn(pomFile = parent_pom_file, phase = phase, **buildKwargs)


def BuildJava(basedir, qualifier, deploy, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.java', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

def BuildEclipse(basedir, qualifier, deploy, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.eclipse', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, forceContextQualifier = qualifier, **kwargs)

def BuildPoms(basedir, deploy, qualifier = None, **kwargs):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.parentpoms', 'pom.xml')
  kwargs.update({'skip-language-build' : True})
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

def BuildSpoofaxLibs(basedir, deploy, qualifier = None, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.libs', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)

def BuildTestRunner(basedir, deploy, qualifier = None, **kwargs):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.testrunner', 'pom.xml')
  Mvn(pomFile = pomFile, phase = phase, **kwargs)


'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
_buildDependencies = OrderedDict([
  ('java'        , []),
  ('eclipse'     , ['java']),
  ('poms'        , ['java', 'eclipse']),
  ('spoofax-libs', ['java']),
  ('test-runner' , ['java']),
])
_buildCommands = {
  'poms'         : BuildPoms,
  'java'         : BuildJava,
  'spoofax-libs' : BuildSpoofaxLibs,
  'test-runner'  : BuildTestRunner,
  'eclipse'      : BuildEclipse,
}

def GetAllBuilds():
  return list(_buildDependencies.keys()) + ['all']

def GetBuildOrder(*args):
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


def CreateQualifier(repo):
  date = LatestDate(repo)
  qualifier = date.strftime('%Y%m%d-%H%M%S')
  return qualifier

def CleanLocalRepo():
  localRepo = path.join(path.expanduser('~'), '.m2', 'repository')
  shutil.rmtree(path.join(localRepo, 'org', 'metaborg'), ignore_errors = True)
  shutil.rmtree(path.join(localRepo, '.cache', 'tycho'), ignore_errors = True)
