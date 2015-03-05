import os
import platform
import subprocess


def Mvn(pomFile = 'pom.xml', settingsFile = None, globalSettingsFile = None, noSnapshotUpdates = False,
        forceSnapshotUpdate = False, offline = False, profiles = [], debug = False, quiet = False,
        extraArgs = None, clean = True, phase = 'verify', resumeFrom = None,
        mavenOpts = '-Xms512m -Xmx1024m -Xss32m -XX:MaxPermSize=512m', **kwargs):
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

  if noSnapshotUpdates:
    args.append('--no-snapshot-updates')
  if forceSnapshotUpdate:
    args.append('--update-snapshots')
  if offline:
    args.append('--offline')

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
