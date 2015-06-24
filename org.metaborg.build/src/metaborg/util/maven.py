import os
import platform
import subprocess
import pystache


def Mvn(pomFile = 'pom.xml', settingsFile = None, globalSettingsFile = None, localRepo = None,
 noSnapshotUpdates = False, forceSnapshotUpdate = False, offline = False, skipTests = False,
 profiles = [], debug = False, quiet = False, extraArgs = None, clean = True, phase = 'verify',
 resumeFrom = None, mavenOpts = '-Xms512m -Xmx2048m -Xss32m -XX:MaxPermSize=512m', **kwargs):
  args = []
  if platform.system() == 'Windows':
    args.append('mvn.bat')
  else:
    args.append('mvn')
  args.append('--batch-mode')

  args.append('--file "{}"'.format(pomFile))
  if settingsFile:
    args.append('--settings "{}"'.format(settingsFile))
  if globalSettingsFile:
    args.append('--global-settings "{}"'.format(globalSettingsFile))
  if localRepo:
    args.append('-Dmaven.repo.local="{}"'.format(localRepo))

  if noSnapshotUpdates:
    args.append('--no-snapshot-updates')
  if forceSnapshotUpdate:
    args.append('--update-snapshots')
  if offline:
    args.append('--offline')
  if skipTests:
    args.append('-Dmaven.test.skip=true')
    args.append('-DskipTests=true')

  if len(profiles) != 0:
    args.append('--activate-profiles={}'.format(','.join(profiles)))

  if debug:
    args.append('--debug')
    args.append('--errors')
  if quiet:
    args.append('--quiet')

  if extraArgs != None:
    args.append(extraArgs)
  for name, value in kwargs.items():
    args.append('-D{}={}'.format(name, value))

  if clean:
    args.append('clean')
  args.append(phase)

  if resumeFrom:
    args.append('--resume-from {}'.format(resumeFrom))

  mvnEnv = os.environ.copy()
  mvnEnv['MAVEN_OPTS'] = mavenOpts
  mvnEnv['CYGWIN'] = 'nodosfilewarning'

  cmd = ' '.join(args)
  print(cmd)
  try:
    process = subprocess.Popen(cmd, env = mvnEnv, shell = True)
    process.communicate()
  except KeyboardInterrupt:
    raise Exception("Maven build interrupted")

  if process.returncode != 0:
    raise Exception("Maven build failed")


def MvnSetingsGen(location, repositories = [], mirrors = []):
  profileDict = {}
  for repo in repositories:
    profileId, repoId, url, layout, releases, snapshots, plugins = repo
    if profileId not in profileDict:
      profileDict[profileId] = []
    profileDict[profileId].append({
      'id'        : repoId,
      'url'       : url,
      'layout'    : layout,
      'releases'  : str(releases).lower(),
      'snapshots' : str(snapshots).lower(),
      'plugins'   : plugins
    })

  profileObjects = []
  for profileId, repos in profileDict.items():
    profileObjects.append({'profileId' : profileId, 'repos' : repos})

  mirrorObjects = []
  for mirror in mirrors:
    mirrorId, url, mirrorOf = mirror
    mirrorObjects.append({'id' : mirrorId, 'url' : url, 'mirrorOf' : mirrorOf})

  settingsTemplate = '''<?xml version="1.0" ?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <profiles>
    {{#profiles}}
    <profile>
      <id>{{profileId}}</id>
      <activation>
        <activeByDefault>true</activeByDefault>
      </activation>
      <repositories>
        {{#repos}}
        <repository>
          <id>{{id}}</id>
          <url>{{url}}</url>
          {{#layout}}<layout>{{layout}}</layout>
          {{/layout}}<releases>
            <enabled>{{releases}}</enabled>
          </releases>
          <snapshots>
            <enabled>{{snapshots}}</enabled>
          </snapshots>
        </repository>
        {{/repos}}
      </repositories>
      <pluginRepositories>
        {{#repos}}{{#plugins}}<pluginRepository>
          <id>{{id}}</id>
          <url>{{url}}</url>
          {{#layout}}<layout>{{layout}}</layout>
          {{/layout}}<releases>
            <enabled>{{releases}}</enabled>
          </releases>
          <snapshots>
            <enabled>{{snapshots}}</enabled>
          </snapshots>
        </pluginRepository>{{/plugins}}{{/repos}}
      </pluginRepositories>
    </profile>
    {{/profiles}}
  </profiles>
  <mirrors>
    {{#mirrors}}
    <mirror>
      <id>{{id}}</id>
      <url>{{url}}</url>
      <mirrorOf>{{mirrorOf}}</mirrorOf>
    </mirror>
    {{/mirrors}}
  </mirrors>
</settings>
'''

  settingsXml = pystache.render(settingsTemplate, { 'profiles' : profileObjects, 'mirrors' : mirrorObjects})
  print('Setting contents of {} to:\n{}'.format(location, settingsXml))
  with open(location, "w") as settingsFile:
    settingsFile.write(settingsXml)

def MvnUserSettingsLocation():
  return os.path.join(os.path.expanduser('~'), '.m2/settings.xml')
