import os
import sys
import platform
import subprocess
import urllib.request
import urllib.parse
import shutil
import zipfile
import re
import requests
import tarfile
from metaborg.util.path import CommonPrefix


def EclipseGen(destination, eclipseOS = None, eclipseWS = None, eclipseArch = None, repositories = [], installUnits = []):
  if eclipseOS == None:
    eclipseOS = CurrentEclipseOS()
  if eclipseWS == None:
    eclipseWS = EclipseWS(eclipseOS)
  if eclipseArch == None:
    eclipseArch = CurrentEclipseArch()

  _DownloadP2Director()

  args = []
  args.append(_DirectorExecutable())
  args.append('-destination {}'.format(destination))
  args.append('-bundlepool {}'.format(destination))
  args.append('-p2.os {}'.format(eclipseOS))
  args.append('-p2.ws {}'.format(eclipseWS))
  args.append('-p2.arch {}'.format(eclipseArch))
  args.append('-tag InitialState')
  args.append('-profile SDKProfile')
  args.append('-profileProperties org.eclipse.update.install.features=true')
  args.append('-roaming')

  if len(repositories) != 0:
    repositories = map(_LocationToURI, repositories)
    args.append('-repository {}'.format(','.join(repositories)))

  if len(installUnits) != 0:
    args.append('-installIU {}'.format(','.join(installUnits)))

  cmd = ' '.join(args)
  print(cmd)
  try:
    process = subprocess.Popen(cmd, shell = True)
    process.communicate()
  except KeyboardInterrupt:
    raise Exception("Eclipse generation interrupted")

  if process.returncode != 0:
    raise Exception("Eclipse generation failed")

def EclipseIniFix(destination, eclipseOS, stackSize = '16M', heapSize = '1G', maxHeapSize = '1G', maxPermGen = '256M',
    requiredJavaVersion = '1.7', server = True):
  iniLocation = _EclipseIniLocation(destination, eclipseOS)

  # Python converts all line endings to '\n' when reading a file in text mode like this.
  with open(iniLocation, "r") as iniFile:
    iniText = iniFile.read()

  iniText = re.sub(r'--launcher\.XXMaxPermSize\n[0-9]+[g|G|m|M|k|K]', '', iniText, flags = re.MULTILINE)
  iniText = re.sub(r'-showsplash\norg.eclipse.platform', '', iniText, flags = re.MULTILINE)

  launcherPattern = r'--launcher\.defaultAction\nopenFile'
  launcherMatches = len(re.findall(launcherPattern, iniText, flags = re.MULTILINE))
  if launcherMatches > 1:
    iniText = re.sub(launcherPattern, '', iniText, count = launcherMatches - 1, flags = re.MULTILINE)

  iniText = re.sub(r'-X(ms|ss|mx)[0-9]+[g|G|m|M|k|K]', '', iniText)
  iniText = re.sub(r'-XX:MaxPermSize=[0-9]+[g|G|m|M|k|K]', '', iniText)
  iniText = re.sub(r'-Dorg\.eclipse\.swt\.internal\.carbon\.smallFonts', '', iniText)
  iniText = re.sub(r'-XstartOnFirstThread', '', iniText)
  iniText = re.sub(r'-Dosgi.requiredJavaVersion=[0-9]\.[0-9]', '', iniText)
  iniText = re.sub(r'-server', '', iniText)

  iniText = '\n'.join([line for line in iniText.split('\n') if line.strip()]) + '\n'

  if eclipseOS == 'macosx':
    iniText += '-XstartOnFirstThread\n'

  if stackSize:
    iniText += '-Xss{}\n'.format(stackSize)
  if heapSize:
    iniText += '-Xms{}\n'.format(heapSize)
  if maxHeapSize:
    iniText += '-Xmx{}\n'.format(maxHeapSize)
  if maxPermGen:
    iniText += '-XX:MaxPermSize={}\n'.format(maxPermGen)

  if requiredJavaVersion:
    iniText += '-Dosgi.requiredJavaVersion={}\n'.format(requiredJavaVersion)

  if server:
    iniText += '-server\n'

  print('Setting contents of {} to:\n{}'.format(iniLocation, iniText))
  with open(iniLocation, "w") as iniFile:
    iniFile.write(iniText)

def EclipseAddJre(destination, eclipseOS = None, eclipseArch = None):
  if eclipseOS == None:
    eclipseOS = CurrentEclipseOS()
  if eclipseArch == None:
    eclipseArch = CurrentEclipseArch()

  jrePath = _DownloadJRE(eclipseOS, eclipseArch)
  targetJrePath = os.path.join(destination, 'jre')
  if os.path.isdir(targetJrePath):
    shutil.rmtree(targetJrePath, ignore_errors=True)
  print('Copying JRE from {} to {}'.format(jrePath, targetJrePath))
  shutil.copytree(jrePath, targetJrePath, symlinks = True)

  relJreLocation = _EclipseJreLocation(eclipseOS)
  iniLocation = _EclipseIniLocation(destination, eclipseOS)
  with open(iniLocation, 'r') as iniFile:
    iniText = iniFile.read()
  with open(iniLocation, 'w') as iniFile:
    print('Prepending VM location {} to eclipse.ini'.format(relJreLocation))
    iniText = re.sub(r'-vm\n.+\n', '', iniText, flags = re.MULTILINE)
    iniFile.write('-vm\n{}\n'.format(relJreLocation) + iniText)


def _EclipseIniLocation(destination, eclipseOS):
  if eclipseOS == 'macosx':
    return '{}/Eclipse.app/Contents/MacOS/eclipse.ini'.format(destination)
  elif eclipseOS == 'linux':
    return '{}/eclipse.ini'.format(destination)
  elif eclipseOS == 'win32':
    return '{}/eclipse.ini'.format(destination)
  else:
    raise Exception('Unsupported Eclipse OS {}'.format(eclipseOS))

def _EclipseJreLocation(eclipseOS):
  if eclipseOS == 'macosx':
    return '../../../jre/Contents/Home/bin/java'
  elif eclipseOS == 'linux':
    return 'jre/bin/java'
  elif eclipseOS == 'win32':
    return 'jre\\bin\\server\\jvm.dll'
  else:
    raise Exception('Unsupported Eclipse OS {}'.format(eclipseOS))


def CurrentEclipseOS():
  system = platform.system()
  if system == 'Darwin':
    return 'macosx'
  elif system == 'Linux':
    return 'linux'
  elif system == 'Windows':
    return 'win32'
  else:
    raise Exception('Unsupported OS {}'.format(system))

def EclipseWS(eclipseOS):
  if eclipseOS == 'macosx':
    return 'cocoa'
  elif eclipseOS == 'linux':
    return 'gtk'
  elif eclipseOS == 'win32':
    return 'win32'
  else:
    raise Exception('Unsupported Eclipse OS {}'.format(eclipseOS))

def CurrentEclipseArch():
  is64Bits = sys.maxsize > 2**32
  if is64Bits:
    return 'x86_64'
  else:
    return 'x86'


def _DownloadP2Director():
  if os.path.isfile(_DirectorExecutable()):
    return

  url = 'http://eclipse.mirror.triple-it.nl/tools/buckminster/products/director_latest.zip'
  directorZipLoc = _EclipsegenLocation('director.zip')
  with urllib.request.urlopen(url) as response, open(directorZipLoc, 'wb') as outFile:
    print('Downloading director from {} to {}'.format(url, directorZipLoc))
    shutil.copyfileobj(response, outFile)
  with zipfile.ZipFile(directorZipLoc) as zipFile:
    unpackLoc = _EclipsegenLocation('director')
    zipFile.extractall(path = unpackLoc)
  os.chmod(_DirectorExecutable(), 0o744)

def _DirectorExecutable():
  if platform.system() == 'Windows':
    return _EclipsegenLocation('director/director/director.bat')
  else:
    return _EclipsegenLocation('director/director/director')


def _DownloadJRE(eclipseOS, eclipseArch):
  version = '7u72'
  urlPrefix = 'http://download.oracle.com/otn-pub/java/jdk/7u72-b14/jre-7u72-'
  extension = 'tar.gz'

  if eclipseOS == 'macosx':
    jreOS = 'macosx'
  elif eclipseOS == 'linux':
    jreOS = 'linux'
  elif eclipseOS == 'win32':
    jreOS = 'windows'
  else:
    raise Exception('Unsupported JRE OS {}'.format(eclipseOS))

  if eclipseArch == 'x86_64':
    jreArch = 'x64'
  elif eclipseArch == 'x86':
    jreArch = 'i586'
  else:
    raise Exception('Unsupported JRE architecture {}'.format(eclipseArch))

  location = _EclipsegenLocation(os.path.join('jre', version))
  os.makedirs(location, exist_ok=True)

  fileName = '{}-{}.{}'.format(jreOS, jreArch, extension)
  filePath = os.path.join(location, fileName)

  dirName = '{}-{}'.format(jreOS, jreArch)
  dirPath = os.path.join(location, dirName)

  if os.path.isdir(dirPath):
    return dirPath

  url = '{}{}'.format(urlPrefix, fileName)
  print('Downloading JRE from {}'.format(url))
  cookies = dict(gpw_e24 = 'http%3A%2F%2Fwww.oracle.com%2F', oraclelicense = 'accept-securebackup-cookie')
  request = requests.get(url, cookies = cookies)
  with open(filePath, 'wb') as file:
    for chunk in request.iter_content(1024):
      file.write(chunk)

  print('Extracting JRE to {}'.format(dirPath))
  with tarfile.open(filePath, 'r') as file:
    file.extractall(path = dirPath)
    rootName = CommonPrefix(file.getnames())
    rootDir = os.path.join(dirPath, rootName)
    for name in os.listdir(rootDir):
      shutil.move(os.path.join(rootDir, name), os.path.join(dirPath, name))
    os.rmdir(rootDir)

  os.remove(filePath)

  return dirPath


def _EclipsegenLocation(location):
  eclipsegenLocation = os.path.join(os.path.expanduser('~'), '.spoofax-releng-eclipsegen')
  if not os.path.isdir(eclipsegenLocation):
    os.mkdir(eclipsegenLocation)
  return '{}/{}'.format(eclipsegenLocation, location)


def _LocationToURI(location):
  if location.startswith('http'):
    return location
  else:
    return urllib.parse.urljoin('file:', urllib.request.pathname2url(location))
