import os
import platform
import subprocess


def Mvn(pomFile = 'pom.xml', clean = True, phase = 'verify', mavenOpts = '-Xms512m -Xmx1024m -Xss32m -XX:MaxPermSize=512m',
        extraArgs = None, **kwargs):
  args = []
  if platform.system() == 'Windows':
    args.append('mvn.bat')
  else:
    args.append('mvn')
  args.append('-B')
  args.append('-f "{}"'.format(pomFile))

  if extraArgs != None:
    args.append(extraArgs)

  for name, value in kwargs.items():
    args.append('-D{}={}'.format(name, value))

  if clean:
    args.append('clean')

  args.append(phase)

  mvnEnv = os.environ.copy()
  mvnEnv['MAVEN_OPTS'] = mavenOpts
  mvnEnv['CYGWIN'] = 'nodosfilewarning'
  cmd = ' '.join(args)
  print(cmd)
  process = subprocess.Popen(cmd, env = mvnEnv)
  process.communicate()
  if process.returncode != 0:
    raise Exception("Maven build failed")
