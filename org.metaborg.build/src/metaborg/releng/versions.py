import os
import xml.etree.ElementTree as ET

from os import path
from metaborg.util.maven import Mvn


def SetVersions(baseDir, oldMavenVersion, newMavenVersion, dryRun = False):
  oldEclipseVersion = oldMavenVersion.replace('-SNAPSHOT', '.qualifier')
  newEclipseVersion = newMavenVersion.replace('-SNAPSHOT', '.qualifier')
  ignoreDirs = ['eclipse-installations', 'target', '_attic']

  print('Old version {} / {}'.format(oldMavenVersion, oldEclipseVersion))
  print('New version {} / {}'.format(newMavenVersion, newEclipseVersion))

  def FindFiles(root, pattern, removeDirs):
    allFiles = []
    for root, dirs, files in os.walk(root):
      for removeDir in removeDirs:
        if removeDir in dirs:
          dirs.remove(removeDir)
      for file in files:
        if file.endswith(pattern):
          allFiles.append(os.path.join(root, file))
    return allFiles

  def ReplaceInFile(file, pattern, replacement):
    print('Setting version in {}'.format(file))
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
  allXmlFiles = FindFiles(baseDir, '.xml', ignoreDirs)
  for xmlFile in allXmlFiles:
    if IsMavenPomFile(xmlFile):
      ReplaceInFile(xmlFile, oldMavenVersion, newMavenVersion)

  print('Setting Maven versions in Spoofax generator files')
  createMavenPomFile = path.join(baseDir, 'spoofax', 'org.strategoxt.imp.generator', 'src', 'sdf2imp', 'project', 'create-maven-pom.str')
  ReplaceInFile(createMavenPomFile, oldMavenVersion, oldMavenVersion)

  print('Setting Eclipse versions in MANIFEST.MF files')
  allManifestFiles = FindFiles(baseDir, 'MANIFEST.MF', ignoreDirs)
  for manifestFile in allManifestFiles:
    ReplaceInFile(manifestFile, oldEclipseVersion, newEclipseVersion)

  print('Setting Eclipse versions in feature.xml files')
  spoofaxDeployDir = path.join(baseDir, 'spoofax-deploy')
  allFeatureFiles = FindFiles(spoofaxDeployDir, 'feature.xml', ignoreDirs)
  for featureFile in allFeatureFiles:
    ReplaceInFile(featureFile, oldEclipseVersion, newEclipseVersion)
