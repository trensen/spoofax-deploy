from datetime import datetime

from metaborg.util.prompt import YesNo, YesNoTwice


def LatestDate(repo):
  date = 0
  for submodule in repo.submodules:
    subrepo = submodule.module()
    head = subrepo.head
    if head.is_detached:
      commitDate = head.commit.committed_date
    else:
      commitDate = head.ref.commit.committed_date

    if commitDate > date:
      date = commitDate

  return datetime.fromtimestamp(date)


def Update(submodule):
  if not submodule.module_exists():
    print('Cannot update {}, it has not been initialized yet. Run "git submodule update --init" first.'.format(submodule.name))
    return

  subrepo = submodule.module()
  remote = subrepo.remote('origin')
  head = subrepo.head
  if head.is_detached:
    print('Cannot update {}, it has a DETACHED HEAD. Resolve the detached head manually or run "checkout" to check out the correct branch.'.format(submodule.name))
#  elif subrepo.is_dirty(untracked_files = False):
#    print('Cannot update {}, it has UNCOMMITTED CHANGES. Resolve the uncommitted changes manually or run "reset" to reset changes.'.format(submodule.name))
#  elif subrepo.is_dirty(untracked_files = True):
#    print('Cannot update {}, it has UNTRACKED FILES. Resolve the untracked files manually or run "clean" to clean untracked files.'.format(submodule.name))
  else:
    print('Updating {} from {}/{}'.format(submodule.name, remote.name, head.reference.name))
    submodule.update(init = False, recursive = True, to_latest_revision = True, keep_going = True)

def UpdateAll(repo):
  print('Updating all submodules')
  for submodule in repo.submodules:
    Update(submodule)


def Checkout(submodule):
  branch = submodule.branch
  print('Switching {} to {}'.format(submodule.name, branch.name))
  branch.checkout()

def CheckoutAll(repo, confirmPrompt = False):
  print('Checking out correct branches for all submodules')
  print('WARNING: This will get rid of detached heads, including any commits you have made to detached heads, do you want to continue?')
  if confirmPrompt or not YesNo():
    return
  for submodule in repo.submodules:
    Checkout(submodule)


def Clean(submodule):
  subrepo = submodule.module()
  print('Cleaning {}'.format(submodule.name))
  subrepo.git.clean('-fd')

def CleanAll(repo, confirmPrompt = False):
  print('Cleaning all submodules')
  print('WARNING: This will DELETE UNTRACKED FILES, do you want to continue?')
  if confirmPrompt or not YesNoTwice():
    return
  for submodule in repo.submodules:
    Clean(submodule)


def Reset(submodule):
  subrepo = submodule.module()
  print('Resetting {}'.format(submodule.name))
  subrepo.git.reset('--hard')

def ResetAll(repo, confirmPrompt = False):
  print('Resetting all submodules')
  print('WARNING: This will DELETE UNCOMMITED CHANGES AND UNPUSHED COMMITS, do you want to continue?')
  if confirmPrompt or not YesNoTwice():
    return
  for submodule in repo.submodules:
    Reset(submodule)
