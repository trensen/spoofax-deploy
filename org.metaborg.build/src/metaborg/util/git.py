from datetime import datetime


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
    print('Cannot update {}, it has not been initialized yet. Run "git submodule update --init --recursive" first.'.format(submodule.name))
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
    submodule.update(init = False, recursive = False, to_latest_revision = True, keep_going = True)

  for submodule in subrepo.submodules:
    Update(submodule)

def UpdateAll(repo):
  for submodule in repo.submodules:
    Update(submodule)


def Checkout(submodule):
  branch = submodule.branch
  print('Switching {} to {}'.format(submodule.name, branch.name))
  branch.checkout()

  subrepo = submodule.module()
  for submodule in subrepo.submodules:
    Checkout(submodule)

def CheckoutAll(repo):
  for submodule in repo.submodules:
    Checkout(submodule)


def Clean(submodule):
  subrepo = submodule.module()
  print('Cleaning {}'.format(submodule.name))
  subrepo.git.clean('-fd')

def CleanAll(repo):
  for submodule in repo.submodules:
    Clean(submodule)


def Reset(submodule):
  subrepo = submodule.module()
  print('Resetting {}'.format(submodule.name))
  subrepo.git.reset('--hard')

def ResetAll(repo):
  for submodule in repo.submodules:
    Reset(submodule)
