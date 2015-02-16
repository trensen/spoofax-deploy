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

  unclean = cli.Flag(names = ['-u', '--unclean'], default = False, help = "Don't clean before building?")
  deploy = cli.Flag(names = ['-d', '--deploy'], default = False, help = 'Deploy after building?')
  buildStratego = cli.Flag(names = ['-s', '--build-stratego'], default = False, help = 'Build StrategoXT?')
  noStrategoTest = cli.Flag(names = ['-t', '--no-stratego-test'], default = False, help = 'Skip StrategoXT tests?')

  def main(self, *args):
    repo = self.parent.repo
    basedir = repo.working_tree_dir

    if len(args) == 0:
      print('No components specified, pass one or more of the following components to build:')
      print(', '.join(GetAllBuilds()))
      return 1

    if not self.unclean:
      CleanLocalRepo()

    if self.buildStratego:
      print('Building StrategoXT')
      BuildStrategoXt(basedir, not self.unclean, self.deploy, not self.noStrategoTest)
    else:
      print('Downloading StrategoXT')
      DownloadStrategoXt(basedir)

    qualifier = CreateQualifier(repo)
    print('Using Eclipse qualifier {}.'.format(qualifier))

    buildOrder = GetBuildOrder(*args)
    print('Building component(s): {}'.format(', '.join(buildOrder)))
    for build in buildOrder:
      print('Building: {}'.format(build))
      cmd = GetBuildCommand(build)
      cmd(basedir, qualifier, not self.unclean, self.deploy)

    print('All done!')


if __name__ == "__main__":
  MetaborgReleng.run()
