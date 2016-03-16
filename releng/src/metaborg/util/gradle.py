import os
import platform
import subprocess
import pystache


def Gradle(cwd=None, useWrapper=True, buildFile='build.gradle', settingsFile=None,
    offline=False, debug=False, stackTrace=False, quiet=False, extraArgs=None, clean=True,
    phase='check',
    # Ignored:
    pomFile=None, globalSettingsFile=None, localRepo=None, noSnapshotUpdates=False,
    forceSnapshotUpdate=False, skipTests=False, profiles=[], resumeFrom=None, mavenOpts=None,
    # Remainder:
    **kwargs):

  # Ignored arguments.
  del pomFile, globalSettingsFile, localRepo, noSnapshotUpdates, forceSnapshotUpdate, skipTests
  del profiles, resumeFrom, mavenOpts

  args = []
  if useWrapper:
    if platform.system() == 'Windows':
      args.append('gradlew')
    else:
      args.append('./gradlew')
  else:
    args.append('gradle')

  if buildFile:
    args.append('--build-file "{}"'.format(buildFile))
  if settingsFile:
    args.append('--settings-file "{}"'.format(settingsFile))

  if offline:
    args.append('--offline')

  if debug:
    args.append('--debug')
  if stackTrace:
    args.append('--stacktrace')
  if quiet:
    args.append('--quiet')
  
  if extraArgs:
    args.append(extraArgs)
  for name, value in kwargs.items():
    args.append('-D{}={}'.format(name, value))

  if clean:
    args.append('clean')
  args.append(phase)

  gradleEnv = os.environ.copy()

  cmd = ' '.join(args)
  print('{}'.format(cmd))
  try:
    process = subprocess.Popen(cmd, cwd=cwd, env=gradleEnv, shell=True)
    process.communicate()
  except KeyboardInterrupt:
    raise RuntimeError("Gradle build interrupted")

  if process.returncode != 0:
    raise RuntimeError("Gradle build failed")

