import os
import xml.etree.ElementTree as ET

from os import path
from metaborg.util.path import CommonPrefix


def SetVersions(repo, oldMavenVersion, newMavenVersion, setEclipseVersions = True, dryRun = False, commit = False):
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
    with open(file) as fileHandle:
      text = fileHandle.read()
    if pattern in text:
      print('Setting version in {}'.format(file))
      text = text.replace(pattern, replacement)
      changedFiles.append(file)
      if dryRun:
        return
      with open(file, "w") as fileHandle:
        fileHandle.write(text)

  def IsMavenPomFile(file):
    try:
      xmlRoot = ET.parse(file)
    except ET.ParseError:
      return False
    project = xmlRoot.getroot()
    if project == None or project.tag != '{http://maven.apache.org/POM/4.0.0}project':
      return False
    return True

  def IsGeneratedManifestFile(file):
    with open(file) as fileHandle:
      text = fileHandle.read()
    return 'Bnd-LastModified' in text

  print('Setting Maven versions in POM files')
  for file in FindFiles(baseDir, '.xml'):
    if IsMavenPomFile(file):
      ReplaceInFile(file, oldMavenVersion, newMavenVersion)

  if setEclipseVersions:
    print('Setting Eclipse versions in MANIFEST.MF files')
    for file in FindFiles(baseDir, 'MANIFEST.MF'):
      if not IsGeneratedManifestFile(file):
        ReplaceInFile(file, oldEclipseVersion, newEclipseVersion)

    print('Setting Eclipse versions in feature.xml files')
    spoofaxDeployDir = path.join(baseDir, 'spoofax-deploy')
    for file in FindFiles(spoofaxDeployDir, 'feature.xml'):
      ReplaceInFile(file, oldEclipseVersion, newEclipseVersion)

    print('Setting Eclipse versions in site.xml files')
    for file in FindFiles(spoofaxDeployDir, 'site.xml'):
      ReplaceInFile(file, oldEclipseVersion, newEclipseVersion)


  if commit:
    print('Committing changed files')
    for submodule in repo.submodules:
      print('Submodule {}'.format(submodule.name))
      subrepo = submodule.module()
      subrepoPath = subrepo.working_dir
      filesToAdd = [path.relpath(f, subrepoPath) for f in changedFiles if CommonPrefix([subrepoPath, f]) == subrepoPath]
      if len(filesToAdd) != 0:
        if dryRun:
          print('Changed files {}'.format(filesToAdd))
        else:
          print('Adding files {} and committing'.format(filesToAdd))
          if len(subrepo.index.add(filesToAdd)) != 0:
            subrepo.index.commit('Set version to {}'.format(newVersionString))
