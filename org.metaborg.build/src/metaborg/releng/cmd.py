from os import path
from git.repo.base import Repo
from plumbum import cli

from metaborg.releng.build import BuildAll, GetAllBuilds
from metaborg.releng.versions import SetVersions
from metaborg.releng.release import Release, ResetRelease
from metaborg.releng.eclipse import GeneratePlainEclipse, GenerateSpoofaxEclipse, GenerateDevSpoofaxEclipse, _eclipseRepo, _eclipsePackage, _spoofaxRepo
from metaborg.util.git import UpdateAll, TrackAll, MergeAll, TagAll, PushAll, CheckoutAll, CleanAll, ResetAll
from metaborg.util.prompt import YesNo, YesNoTwice, YesNoTrice
from metaborg.util.path import CommonPrefix


class MetaborgReleng(cli.Application):
  PROGNAME = 'releng'
  VERSION = '1.4.0'

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


@MetaborgReleng.subcommand("track")
class MetaborgRelengTrack(cli.Application):
  '''
  Sets tracking branch to submodule remote branch for each submodule
  '''

  def main(self):
    print('Setting tracking branch for each submodule')
    TrackAll(self.parent.repo)
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
    ResetAll(self.parent.repo, self.toRemote)
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
                           help = 'Build StrategoXT instead of downloading it')
  bootstrapStratego = cli.Flag(names = ['-b', '--bootstrap-stratego'], default = False,
                               help = 'Bootstrap StrategoXT instead of building it')
  noStrategoTest = cli.Flag(names = ['-t', '--no-stratego-test'], default = False,
                            help = 'Skip StrategoXT tests')

  noCleanRepo = cli.Flag(names = ['-p', '--no-clean-repo'], default = False,
                         help = 'Do not clean local repository before building')
  noDeps = cli.Flag(names = ['-e', '--no-deps'], default = False, requires = ['--no-clean-repo'],
                    help = 'Do not build dependencies, just build given components')
  resumeFrom = cli.SwitchAttr(names = ['-f', '--resume-from'], argtype = str, default = None,
                              requires = ['--no-clean-repo', '--no-deps'], help = 'Resume build from given artifact')
  deploy = cli.Flag(names = ['-d', '--deploy'], default = False,
                    help = 'Deploy after building')
  release = cli.Flag(names = ['-r', '--release'], default = False,
                     help = 'Perform a release build. Checks whether all dependencies are release versions, fails the build if not')

  noClean = cli.Flag(names = ['-u', '--no-clean'], default = False,
                     help = 'Do not run the clean phase in Maven builds')
  offline = cli.Flag(names = ['-o', '--offline'], default = False,
                     help = "Pass --offline flag to Maven")
  debug = cli.Flag(names = ['-x', '--debug'], default = False, excludes = ['--quiet'],
                   help = "Pass --debug flag to Maven")
  quiet = cli.Flag(names = ['-q', '--quiet'], default = False, excludes = ['--debug'],
                   help = "Pass --quiet flag to Maven")

  def main(self, *components):
    if len(components) == 0:
      print('No components specified, pass one or more of the following components to build:')
      print(', '.join(GetAllBuilds()))
      return 1

    repo = self.parent.repo

    try:
      BuildAll(repo = repo, components = components, buildDeps = not self.noDeps, resumeFrom = self.resumeFrom,
        buildStratego = self.buildStratego, bootstrapStratego = self.bootstrapStratego,
        strategoTest = not self.noStrategoTest, cleanRepo = not self.noCleanRepo, release = self.release,
        deploy = self.deploy, clean = not self.noClean, offline = self.offline, debug = self.debug, quiet = self.quiet)
      print('All done!')
      return 0
    except Exception as detail:
      print(str(detail))
      return 1


@MetaborgReleng.subcommand("release")
class MetaborgRelengRelease(cli.Application):
  '''
  Performs an interactive release
  '''

  releaseBranch = cli.SwitchAttr(names = ['--rel-branch'], argtype = str, mandatory = True,
                                 help = "Release branch")
  developBranch = cli.SwitchAttr(names = ['--dev-branch'], argtype = str, mandatory = True,
                                 help = "Development branch")

  curDevelopVersion = cli.SwitchAttr(names = ['--cur-dev-ver'], argtype = str, mandatory = True,
                                     help = "Current Maven version in the development branch")
  nextReleaseVersion = cli.SwitchAttr(names = ['--next-rel-ver'], argtype = str, mandatory = True,
                                      help = "Next Maven version in the release branch")
  nextDevelopVersion = cli.SwitchAttr(names = ['--next-dev-ver'], argtype = str, mandatory = True,
                                      help = "Next Maven version in the development branch")

  def main(self):
    print('Performing interactive release')

    repo = self.parent.repo
    repoDir = repo.working_tree_dir
    scriptDir = path.dirname(path.realpath(__file__))
    if CommonPrefix([repoDir, scriptDir]) == repoDir:
      print('Cannot perform release on the same repository this script is contained in, please set another repository using the -r/--repo switch.')
      return 1

    Release(repo, self.releaseBranch, self.developBranch, self.curDevelopVersion, self.nextReleaseVersion, self.nextDevelopVersion)
    return 0


@MetaborgReleng.subcommand("gen-eclipse")
class MetaborgRelengGenEclipse(cli.Application):
  '''
  Generate a plain Eclipse instance
  '''

  destination =    cli.SwitchAttr(names = ['-d', '--destination'],  argtype = str, mandatory = True,                             help = 'Path to generate the Eclipse instance at')
  eclipsePackage = cli.SwitchAttr(names = ['--eclipse-package'],    argtype = str, mandatory = False, default = _eclipsePackage, help = 'Base Eclipse package to install')
  eclipseRepo =    cli.SwitchAttr(names = ['--eclipse-repository'], argtype = str, mandatory = False, default = _eclipseRepo,    help = 'Eclipse repository used to install the base Eclipse package')

  def main(self):
    print('Generating plain Eclipse instance')

    GeneratePlainEclipse(self.destination, eclipsePackage = self.eclipsePackage, eclipseRepo = self.eclipseRepo)
    return 0


@MetaborgReleng.subcommand("gen-spoofax")
class MetaborgRelengGenSpoofax(cli.Application):
  '''
  Generate an Eclipse instance for Spoofax users
  '''

  destination =    cli.SwitchAttr(names = ['-d', '--destination'],  argtype = str, mandatory = True,                             help = 'Path to generate the Eclipse instance at')
  eclipsePackage = cli.SwitchAttr(names = ['--eclipse-package'],    argtype = str, mandatory = False, default = _eclipsePackage, help = 'Base Eclipse package to install')
  eclipseRepo =    cli.SwitchAttr(names = ['--eclipse-repository'], argtype = str, mandatory = False, default = _eclipseRepo,    help = 'Eclipse repository used to install the base Eclipse package')
  spoofaxRepo =    cli.SwitchAttr(names = ['--spoofax-repository'], argtype = str, mandatory = False, default = _spoofaxRepo,    help = 'Spoofax repository used to install Spoofax plugins')

  noMeta =      cli.Flag(names = ['-m', '--nometa'],      default = False, help = "Don't install Spoofax meta-plugins such as the Stratego compiler and editor. Results in a smaller Eclipse instance, but it can only be used to run Spoofax languages, not develop them.")
  noModelware = cli.Flag(names = ['-w', '--nomodelware'], default = False, help = "Don't install Spoofax modelware plugins. Results in a smaller Eclipse instance, but modelware components cannot be used.")

  def main(self):
    print('Generating Eclipse instance for Spoofax users')

    GenerateSpoofaxEclipse(self.destination, eclipsePackage = self.eclipsePackage, eclipseRepo = self.eclipseRepo,
                           spoofaxRepo = self.spoofaxRepo, installMeta = not self.noMeta,
                           installModelware = not self.noModelware)
    return 0


@MetaborgReleng.subcommand("gen-dev-spoofax")
class MetaborgRelengGenDevSpoofax(cli.Application):
  '''
  Generate an Eclipse instance for Spoofax developers
  '''

  destination =    cli.SwitchAttr(names = ['-d', '--destination'],  argtype = str, mandatory = True,                             help = 'Path to generate the Eclipse instance at')
  eclipsePackage = cli.SwitchAttr(names = ['--eclipse-package'],    argtype = str, mandatory = False, default = _eclipsePackage, help = 'Base Eclipse package to install')
  eclipseRepo =    cli.SwitchAttr(names = ['--eclipse-repository'], argtype = str, mandatory = False, default = _eclipseRepo,    help = 'Eclipse repository used to install the base Eclipse package')
  spoofaxRepo =    cli.SwitchAttr(names = ['--spoofax-repository'], argtype = str, mandatory = False, default = _spoofaxRepo,    help = 'Spoofax repository used to install Spoofax plugins')

  def main(self):
    print('Generating Eclipse instance for Spoofax developers')

    GenerateDevSpoofaxEclipse(self.destination, eclipsePackage = self.eclipsePackage, eclipseRepo = self.eclipseRepo,
                              spoofaxRepo = self.spoofaxRepo)
    return 0
