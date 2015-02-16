from collections import OrderedDict
from os import path
import shutil

from metaborg.util.git import LatestDate
from metaborg.util.maven import Mvn


def DownloadStrategoXt(basedir):
  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile, False, 'dependency:resolve')

def BuildStrategoXt(basedir, clean, deploy, runTests):
  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')
  phase = 'deploy' if deploy else 'install'

  pomFile = path.join(strategoXtDir, 'build-pom.xml')
  Mvn(pomFile, clean, phase, **{'strategoxt-skip-test': not runTests})

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  Mvn(parent_pom_file, clean, phase, **{'strategoxt-skip-build': 'true', 'strategoxt-skip-assembly' : 'true'})


def BuildJava(basedir, qualifier, clean, deploy):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.java', 'pom.xml')
  Mvn(pomFile, clean, phase, forceContextQualifier = qualifier)

def BuildEclipse(basedir, qualifier, clean, deploy):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.eclipse', 'pom.xml')
  Mvn(pomFile, clean, phase, forceContextQualifier = qualifier)

def BuildPoms(basedir, qualifier, clean, deploy):
  phase = 'deploy' if deploy else 'install'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.parentpoms', 'pom.xml')
  Mvn(pomFile, clean, phase, **{'skip-language-build' : 'true'})

def BuildSpoofaxLibs(basedir, qualifier, clean, deploy):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.libs', 'pom.xml')
  Mvn(pomFile, clean, phase)

def BuildTestRunner(basedir, qualifier, clean, deploy):
  phase = 'deploy' if deploy else 'verify'
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.testrunner', 'pom.xml')
  Mvn(pomFile, clean, phase)


'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
_buildDependencies = OrderedDict([
  ('java', []),
  ('eclipse', ['java']),
  ('poms', ['java', 'eclipse']),
  ('spoofax-libs', ['java']),
  ('test-runner', ['java']),
])
_buildCommands = {
  'poms' : BuildPoms,
  'java': BuildJava,
  'spoofax-libs' : BuildSpoofaxLibs,
  'test-runner' : BuildTestRunner,
  'eclipse': BuildEclipse,
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
