from git.repo.base import Repo
from plumbum import cli

from metaborg.releng.build import BuildStrategoXt, DownloadStrategoXt, CleanLocalRepo, CreateQualifier, GetBuildOrder, GetBuildCommand, GetAllBuilds
from metaborg.util.git import UpdateAll, CheckoutAll, CleanAll, ResetAll


class MetaborgReleng(cli.Application):
  PROGNAME = 'releng'
  VERSION = '1.3.0'

  repoDirectory = '.'

  repo = None

  @cli.switch(names = ["--repo", "-r"], argtype = str)
  def repo_directory(self, directory):
    '''
    Sets the spoofax-releng repository to operate on
    Defaults to the current directory
    '''
    self.repoDirectory = directory

  def main(self):
    if not self.nested_command:
      print('Error: no command given')
      self.help()
      return 1

    cli.ExistingDirectory(self.repoDirectory)

    self.repo = Repo(self.repoDirectory)

@MetaborgReleng.subcommand("update")
class MetaborgRelengUpdate(cli.Application):
  '''Updates all submodules to the latest commit on the remote repository'''

  def main(self):
    UpdateAll(self.parent.repo)

@MetaborgReleng.subcommand("checkout")
class MetaborgRelengCheckout(cli.Application):
  '''
  Checks out the correct branches for each submodule.
  WARNING: This will get rid of detached heads, including any commits you have made to detached heads
  '''

  confirmPrompt = cli.Flag(names = ['-c', '--confirm'], default = False,
                           help = 'Answer warning prompt automatically with yes?')

  def main(self):
    CheckoutAll(self.parent.repo, self.confirmPrompt)

@MetaborgReleng.subcommand("clean")
class MetaborgRelengClean(cli.Application):
  '''
  Cleans untracked files in each submodule.
  WARNING: This will DELETE UNTRACKED FILES
  '''

  confirmPrompt = cli.Flag(names = ['-c', '--confirm'], default = False,
                           help = 'Answer warning prompt automatically with yes?')

  def main(self):
    CleanAll(self.parent.repo, self.confirmPrompt)

@MetaborgReleng.subcommand("reset")
class MetaborgRelengReset(cli.Application):
  '''
  Resets each submodule.
  WARNING: This will DELETE UNCOMMITED CHANGES AND UNPUSHED COMMITS
  '''

  confirmPrompt = cli.Flag(names = ['-c', '--confirm'], default = False,
                           help = 'Answer warning prompt automatically with yes?')

  def main(self):
    ResetAll(self.parent.repo, self.confirmPrompt)

@MetaborgReleng.subcommand("build")
class MetaborgRelengBuild(cli.Application):
  '''Builds one or more components of spoofax-releng'''

  buildStratego = cli.Flag(names = ['-s', '--build-stratego'], default = False,
                           help = 'Build StrategoXT?')
  noStrategoTest = cli.Flag(names = ['-t', '--no-stratego-test'], default = False,
                            help = 'Skip StrategoXT tests?')

  noClean = cli.Flag(names = ['-u', '--no-clean'], default = False,
                     help = "Don't clean before building?")
  deploy = cli.Flag(names = ['-d', '--deploy'], default = False,
                    help = 'Deploy after building?')
  release = cli.Flag(names = ['-r', '--release'], default = False,
                     help = 'Perform a release build? Checks whether all dependencies are release versions, fails the build if not')

  offline = cli.Flag(names = ['-o', '--offline'], default = False,
                     help = "Pass --offline flag to Maven?")
  debug = cli.Flag(names = ['-b', '--debug'], default = False,
                   help = "Pass --debug flag to Maven?")
  quiet = cli.Flag(names = ['-q', '--quiet'], default = False,
                   help = "Pass --quiet flag to Maven?")

  def main(self, *args):
    if len(args) == 0:
      print('No components specified, pass one or more of the following components to build:')
      print(', '.join(GetAllBuilds()))
      return 1

    repo = self.parent.repo
    basedir = repo.working_tree_dir
    clean = not self.noClean
    profiles = []
    if self.release:
      profiles.append('release')

    if clean:
      CleanLocalRepo()

    if self.buildStratego:
      print('Building StrategoXT')
      BuildStrategoXt(basedir = basedir, deploy = self.deploy, runTests = not self.noStrategoTest,
                      clean = clean, noSnapshotUpdates = True, profiles = profiles, debug = self.debug,
                      quiet = self.quiet)
    else:
      print('Downloading StrategoXT')
      DownloadStrategoXt(basedir = basedir)

    profiles.append('!add-metaborg-repositories')

    qualifier = CreateQualifier(repo)
    print('Using Eclipse qualifier {}.'.format(qualifier))

    buildOrder = GetBuildOrder(*args)
    print('Building component(s): {}'.format(', '.join(buildOrder)))
    for build in buildOrder:
      print('Building: {}'.format(build))
      cmd = GetBuildCommand(build)
      cmd(basedir = basedir, qualifier = qualifier, deploy = self.deploy, clean = clean,
          noSnapshotUpdates = True, profiles = profiles, offline = self.offline,
          debug = self.debug, quiet = self.quiet)

    print('All done!')
