import os
import xml.etree.ElementTree as ET

from os import path
from metaborg.util.maven import Mvn


def SetVersions(repo, oldMavenVersion, newMavenVersion, dryRun = False, commit = False):
  baseDir = repo.working_tree_dir
  ignoreDirs = ['eclipse-installations', 'target', '_attic']

  oldEclipseVersion = oldMavenVersion.replace('-SNAPSHOT', '.qualifier')
  newEclipseVersion = newMavenVersion.replace('-SNAPSHOT', '.qualifier')
  if oldEclipseVersion == oldMavenVersion:
    oldVersionString = oldMavenVersion
  else:
    oldVersionString = '{} / {}'.format(oldMavenVersion, oldEclipseVersion)
  if newEclipseVersion == newMavenVersion:
    newVersionString = newMavenVersion
  else:
    newVersionString = '{} / {}'.format(newMavenVersion, newEclipseVersion)

  changedFiles = []

  print('Old version {}'.format(oldVersionString))
  print('New version {}'.format(newVersionString))

  def FindFiles(root, pattern):
    allFiles = []
    for rootDir, dirs, files in os.walk(root):
      for ignoreDir in ignoreDirs:
        if ignoreDir in dirs:
          dirs.remove(ignoreDir)
      for file in files:
        if file.endswith(pattern):
          allFiles.append(os.path.join(rootDir, file))
    return allFiles

  def ReplaceInFile(file, pattern, replacement):
    print('Setting version in {}'.format(file))
    changedFiles.append(file)
    if dryRun:
      return
    with open(file) as fileHandle:
      text = fileHandle.read()
    text = text.replace(pattern, replacement)
    with open(file, "w") as fileHandle:
      fileHandle.write(text)

  def IsMavenPomFile(file):
    try:
      xmlRoot = ET.parse(xmlFile)
    except ET.ParseError:
      return False
    project = xmlRoot.getroot()
    if project == None or project.tag != '{http://maven.apache.org/POM/4.0.0}project':
      return False
    return True

  print('Setting Maven versions in POM files')
  allXmlFiles = FindFiles(baseDir, '.xml')
  for xmlFile in allXmlFiles:
    if IsMavenPomFile(xmlFile):
      ReplaceInFile(xmlFile, oldMavenVersion, newMavenVersion)

  print('Setting Maven versions in Spoofax generator files')
  createMavenPomFile = path.join(baseDir, 'spoofax', 'org.strategoxt.imp.generator', 'src', 'sdf2imp', 'project', 'create-maven-pom.str')
  ReplaceInFile(createMavenPomFile, oldMavenVersion, oldMavenVersion)

  print('Setting Eclipse versions in MANIFEST.MF files')
  allManifestFiles = FindFiles(baseDir, 'MANIFEST.MF')
  for manifestFile in allManifestFiles:
    ReplaceInFile(manifestFile, oldEclipseVersion, newEclipseVersion)

  print('Setting Eclipse versions in feature.xml files')
  spoofaxDeployDir = path.join(baseDir, 'spoofax-deploy')
  allFeatureFiles = FindFiles(spoofaxDeployDir, 'feature.xml')
  for featureFile in allFeatureFiles:
    ReplaceInFile(featureFile, oldEclipseVersion, newEclipseVersion)

  if commit:
    print('Committing changed files')
    for submodule in repo.submodules:
      print('Submodule {}'.format(submodule.name))
      subrepo = submodule.module()
      subrepoPath = subrepo.working_dir
      filesToAdd = [path.relpath(f, subrepoPath) for f in changedFiles if path.commonprefix([subrepoPath, f]) == subrepoPath]
      print('Adding files {} and committing'.format(filesToAdd))
      if not dryRun:
        subrepo.index.add(filesToAdd)
        subrepo.index.commit('Set version to {}'.format(newVersionString))
