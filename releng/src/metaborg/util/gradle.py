import os
import platform
import subprocess
import pystache


def Gradle(cwd=None, useWrapper=True, buildFile='build.gradle', gradleSettingsFile=None,
    offline=False, debug=False, stackTrace=False, quiet=False, extraArgs=None, clean=True,
    phase='check', native=False,
    # Ignored:
    pomFile=None, settingsFile=None, globalSettingsFile=None, localRepo=None, noSnapshotUpdates=False,
    forceSnapshotUpdate=False, skipTests=False, profiles=[], resumeFrom=None, mavenOpts=None,
    # Remainder:
    **kwargs):

  # Ignored arguments.
  del pomFile, settingsFile, globalSettingsFile, localRepo, noSnapshotUpdates, forceSnapshotUpdate
  del skipTests, profiles, resumeFrom, mavenOpts

  args = []
  if useWrapper:
    if platform.system() == 'Windows':
      args.append('gradlew')
    else:
      args.append('./gradlew')
  else:
    args.append('gradle')

  # Must occur before --build-file, for some reason. Gradle bug?
  if not native:
	# Based on this: https://github.com/adammurdoch/native-platform/issues/6#issuecomment-41315984
    args.append('-Dorg.gradle.native=false')

  if buildFile:
    args.append('--build-file "{}"'.format(buildFile))
  if gradleSettingsFile:
    args.append('--settings-file "{}"'.format(gradleSettingsFile))

  if offline:
    args.append('--offline')

  if stackTrace:
    args.append('--stacktrace')
  if debug:
    args.append('--debug')
  elif quiet:
    args.append('--quiet')
  else:
    args.append('--info')
  
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

