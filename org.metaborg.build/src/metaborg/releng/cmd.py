from git.repo.base import Repo
from plumbum import cli

from metaborg.releng.build import BuildStrategoXt, DownloadStrategoXt, CleanLocalRepo, CreateQualifier, GetBuildOrder, GetBuildCommand, GetAllBuilds
from metaborg.releng.versions import SetVersions
from metaborg.util.git import UpdateAll, MergeAll, TagAll, PushAll, CheckoutAll, CleanAll, ResetAll
from metaborg.util.prompt import YesNo, YesNoTwice, YesNoTrice


class MetaborgReleng(cli.Application):
  PROGNAME = 'releng'
  VERSION = '1.3.0'

  repoDirectory = '.'
  repo = None

  @cli.switch(names = ["--repo", "-r"], argtype = str)
  def repo_directory(self, directory):
    '''
    Sets the spoofax-releng repository to operate on.
    Defaults to the current directory if not set
    '''
    self.repoDirectory = directory

  def main(self):
    if not self.nested_command:
      print('Error: no command given')
      self.help()
      return 1
    cli.ExistingDirectory(self.repoDirectory)

    self.repo = Repo(self.repoDirectory)
    return 0


@MetaborgReleng.subcommand("update")
class MetaborgRelengUpdate(cli.Application):
  '''
  Updates all submodules to the latest commit on the remote repository
  '''

  def main(self):
    print('Updating all submodules')
    UpdateAll(self.parent.repo)
    return 0


@MetaborgReleng.subcommand("merge")
class MetaborgRelengMerge(cli.Application):
  '''
  Merges a branch into the current branch for each submodule
  '''

  branch = cli.SwitchAttr(names = ['-b', '--branch'], argtype = str, mandatory = True,
                          help = 'Branch to merge')

  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    print('Merging branch into current branch for each submodule')
    if not self.confirmPrompt:
      print('This will merge branches, changing the state of your repositories, do you want to continue?')
      if not YesNo():
        return 1
    MergeAll(self.parent.repo, self.branch)
    return 0


@MetaborgReleng.subcommand("tag")
class MetaborgRelengTag(cli.Application):
  '''
  Creates a tag in each submodule
  '''

  tag = cli.SwitchAttr(names = ['-n', '--name'], argtype = str, mandatory = True,
                       help = 'Name of the tag')
  description = cli.SwitchAttr(names = ['-d', '--description'], argtype = str, mandatory = False, default = None,
                       help = 'Description of the tag')

  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    print('Creating a tag in each submodules')
    if not self.confirmPrompt:
      print('This creates tags, changing the state of your repositories, do you want to continue?')
      if not YesNo():
        return 1
    TagAll(self.parent.repo, self.tag, self.description)
    return 0


@MetaborgReleng.subcommand("push")
class MetaborgRelengPush(cli.Application):
  '''
  Pushes the current branch for each submodule
  '''

  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    print('Pushing current branch for each submodule')
    if not self.confirmPrompt:
      print('This pushes commits to the remote repository, do you want to continue?')
      if not YesNo():
        return 1
    PushAll(self.parent.repo)
    return 0


@MetaborgReleng.subcommand("checkout")
class MetaborgRelengCheckout(cli.Application):
  '''
  Checks out the correct branches for each submodule
  '''

  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    print('Checking out correct branches for all submodules')
    if not self.confirmPrompt:
      print('WARNING: This will get rid of detached heads, including any commits you have made to detached heads, do you want to continue?')
      if not YesNo():
        return 1
    CheckoutAll(self.parent.repo)
    return 0


@MetaborgReleng.subcommand("clean")
class MetaborgRelengClean(cli.Application):
  '''
  Cleans untracked files in each submodule
  '''

  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    print('Cleaning all submodules')
    if not self.confirmPrompt:
      print('WARNING: This will DELETE UNTRACKED FILES, do you want to continue?')
      if not YesNoTwice():
        return 1
    CleanAll(self.parent.repo)
    return 0


@MetaborgReleng.subcommand("reset")
class MetaborgRelengReset(cli.Application):
  '''
  Resets each submodule
  '''

  toRemote = cli.Flag(names = ['-r', '--remote'], default = False,
                      help = 'Resets to the remote branch, deleting any unpushed commits')

  def main(self):
    print('Resetting all submodules')
    if self.toRemote:
      print('WARNING: This will DELETE UNCOMMITED CHANGES and DELETE UNPUSHED COMMITS, do you want to continue?')
      if not YesNoTrice():
        return 1
    else:
      print('WARNING: This will DELETE UNCOMMITED CHANGES, do you want to continue?')
      if not YesNoTwice():
        return 1
    ResetAll(self.parent.repo)
    return 0


@MetaborgReleng.subcommand("set-versions")
class MetaborgRelengSetVersions(cli.Application):
  '''
  Sets Maven and Eclipse version numbers to given version number
  '''

  fromVersion = cli.SwitchAttr(names = ['-f', '--from'], argtype = str, mandatory = True,
                               help = 'Maven version to change from')
  toVersion = cli.SwitchAttr(names = ['-t', '--to'], argtype = str, mandatory = True,
                             help = 'Maven version to change from')

  commit = cli.Flag(names = ['-c', '--commit'], default = False,
                    help = 'Commit changed files')
  dryRun = cli.Flag(names = ['-d', '--dryrun'], default = False,
                    help = 'Do not modify or commit files, just print operations')
  confirmPrompt = cli.Flag(names = ['-y', '--yes'], default = False,
                           help = 'Answer warning prompts with yes automatically')

  def main(self):
    if not self.confirmPrompt and not self.dryRun:
      if self.commit:
        print('WARNING: This will CHANGE and COMMIT pom.xml, MANIFEST.MF, and feature.xml files, do you want to continue?')
      else:
        print('WARNING: This will CHANGE pom.xml, MANIFEST.MF, and feature.xml files, do you want to continue?')
        if not YesNo():
          return 1
    SetVersions(self.parent.repo, self.fromVersion, self.toVersion, self.dryRun, self.commit)
    return 0


@MetaborgReleng.subcommand("build")
class MetaborgRelengBuild(cli.Application):
  '''
  Builds one or more components of spoofax-releng
  '''

  buildStratego = cli.Flag(names = ['-s', '--build-stratego'], default = False,
                           help = 'Build StrategoXT')
  noStrategoTest = cli.Flag(names = ['-t', '--no-stratego-test'], default = False,
                            help = 'Skip StrategoXT tests')

  noClean = cli.Flag(names = ['-u', '--no-clean'], default = False,
                     help = "Do not clean before building")
  deploy = cli.Flag(names = ['-d', '--deploy'], default = False,
                    help = 'Deploy after building')
  release = cli.Flag(names = ['-r', '--release'], default = False,
                     help = 'Perform a release build. Checks whether all dependencies are release versions, fails the build if not')

  offline = cli.Flag(names = ['-o', '--offline'], default = False,
                     help = "Pass --offline flag to Maven")
  debug = cli.Flag(names = ['-b', '--debug'], default = False,
                   help = "Pass --debug flag to Maven")
  quiet = cli.Flag(names = ['-q', '--quiet'], default = False,
                   help = "Pass --quiet flag to Maven")

  def main(self, *components):
    if len(components) == 0:
      print('No components specified, pass one or more of the following components to build:')
      print(', '.join(GetAllBuilds()))
      return 1

    repo = self.parent.repo
    basedir = repo.working_tree_dir
    clean = not self.noClean
    profiles = []
    if self.release:
      profiles.append('release')

    try:
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

      buildOrder = GetBuildOrder(*components)
      print('Building component(s): {}'.format(', '.join(buildOrder)))
      for build in buildOrder:
        print('Building: {}'.format(build))
        cmd = GetBuildCommand(build)
        cmd(basedir = basedir, qualifier = qualifier, deploy = self.deploy, clean = clean,
            noSnapshotUpdates = True, profiles = profiles, offline = self.offline,
            debug = self.debug, quiet = self.quiet)
      print('All done!')
      return 0
    except Exception as detail:
      print(detail)
      return 1
