from os import path
import shutil

from metaborg.util.git import LatestDate
from metaborg.util.maven import Mvn


def DownloadStrategoXt(basedir):
  pomFile = path.join(basedir, 'strategoxt', 'strategoxt', 'download-pom.xml')
  Mvn(pomFile, False, 'dependency:resolve')

def BuildStrategoXt(basedir, clean = True, phase = 'install', runTests = True):
  strategoXtDir = path.join(basedir, 'strategoxt', 'strategoxt')

  pomFile = path.join(strategoXtDir, 'build-pom.xml')
  Mvn(pomFile, clean, phase, **{'strategoxt-skip-test': not runTests})

  parent_pom_file = path.join(strategoXtDir, 'buildpoms', 'pom.xml')
  Mvn(parent_pom_file, clean, phase, **{'strategoxt-skip-build': 'true', 'strategoxt-skip-assembly' : 'true'})


def BuildJava(basedir, qualifier, clean = True, phase = 'install'):
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.java', 'pom.xml')
  Mvn(pomFile, clean, phase, forceContextQualifier = qualifier)

def BuildEclipse(basedir, qualifier, clean = True, phase = 'install'):
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.eclipse', 'pom.xml')
  Mvn(pomFile, clean, phase, forceContextQualifier = qualifier)

def BuildPoms(basedir, qualifier, clean = True, phase = 'install'):
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.parentpoms', 'pom.xml')
  Mvn(pomFile, clean, phase, **{'skip-language-build' : 'true'})

def BuildSpoofaxLibs(basedir, qualifier, clean = True, phase = 'verify'):
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.libs', 'pom.xml')
  Mvn(pomFile, clean, phase)

def BuildTestRunner(basedir, qualifier, clean = True, phase = 'verify'):
  pomFile = path.join(basedir, 'spoofax-deploy', 'org.metaborg.maven.build.spoofax.testrunner', 'pom.xml')
  Mvn(pomFile, clean, phase)


buildComps = ['java', 'eclipse', 'poms', 'spoofax-libs', 'test-runner']
'''Build dependencies must be topologically ordered, otherwise the algorithm will not work'''
buildDeps = {
             'java': [],
             'eclipse': ['java'],
             'poms' : ['java', 'eclipse'],
             'spoofax-libs' : ['java'],
             'test-runner' : ['java'],
}
buildCmds = {
             'poms' : BuildPoms,
             'java': BuildJava,
             'spoofax-libs' : BuildSpoofaxLibs,
             'test-runner' : BuildTestRunner,
             'eclipse': BuildEclipse,
             }

def GetBuilds(*args):
  if 'all' in args:
    return buildComps

  builds = set()
  for name, deps in buildDeps.items():
    if name in args:
      builds.add(name)
      for dep in deps:
        builds.add(dep)
  return builds

def Qualifier(repo):
  date = LatestDate(repo)
  qualifier = date.strftime('%Y%m%d-%H%M%S')
  return qualifier

def CleanLocalRepo():
  localRepo = path.join(path.expanduser('~'), '.m2', 'repository')
  shutil.rmtree(path.join(localRepo, 'org', 'metaborg'), ignore_errors = True)
  shutil.rmtree(path.join(localRepo, '.cache', 'tycho'), ignore_errors = True)

def Build(repo, clean = True, phase = 'verify', *args):
  qualifier = Qualifier(repo)
  print('Using Eclipse qualifier {}.'.format(qualifier))

  builds = GetBuilds(*args)
  for name in buildDeps.keys():
    if name in builds:
      cmd = buildCmds[name]
      print('Building {}'.format(name))
      cmd(basedir = repo.working_tree_dir, qualifier = qualifier, clean = clean, phase = phase)
