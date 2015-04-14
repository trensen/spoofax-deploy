import os
import sys
import platform
import subprocess
import urllib.request
import urllib.parse
import shutil
import zipfile
import re


def EclipseGen(destination, eclipseOS = None, eclipseWS = None, eclipseArch = None, repositories = [], installUnits = []):
  if not os.path.isfile(_DirectorExecutable()):
    _DownloadP2Director()

  args = []
  args.append(_DirectorExecutable())

  args.append('-destination {}'.format(destination))
  args.append('-bundlepool {}'.format(destination))

  if eclipseOS == None:
    eclipseOS = CurrentEclipseOS()
  args.append('-p2.os {}'.format(eclipseOS))

  if eclipseWS == None:
    eclipseWS = CurrentEclipseWS()
  args.append('-p2.ws {}'.format(eclipseWS))

  if eclipseArch == None:
    eclipseArch = CurrentEclipseArch()
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

def _EclipseIniLocation(destination, eclipseOS):
    if eclipseOS == 'macosx':
      return '{}/Eclipse.app/Contents/MacOS/eclipse.ini'.format(destination)
    elif eclipseOS == 'linux':
      return '{}/eclipse.ini'.format(destination)
    elif eclipseOS == 'win32':
      return '{}/eclipse.ini'.format(destination)


def CurrentEclipseOS():
  system = platform.system()
  if system == 'Darwin':
    return 'macosx'
  elif system == 'Linux':
    return 'linux'
  elif system == 'Windows':
    return 'win32'

def CurrentEclipseWS():
  system = platform.system()
  if system == 'Darwin':
    return 'cocoa'
  elif system == 'Linux':
    return 'gtk'
  elif system == 'Windows':
    return 'win32'

def CurrentEclipseArch():
  is64Bits = sys.maxsize > 2**32
  if is64Bits:
    return 'x86_64'
  else:
    return 'x86'


def _DownloadP2Director():
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


if __name__ == "__main__":
  try:
    EclipseIniFix('/Users/gohla/spoofax/eclipse/generated', 'macosx')
  except KeyboardInterrupt as detail:
    print(detail)
