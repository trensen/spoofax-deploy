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


def Merge(submodule, branchName):
  subrepo = submodule.module()
  head = subrepo.head
  if head.is_detached:
    print('Cannot merge, {} has a DETACHED HEAD.'.format(submodule.name))
    return
  branch = subrepo.heads[branchName]
  if branch == None:
    print('Cannot merge, branch {} does not exist'.format(branchName))
    return
  print('Merging branch {} into {} in {}'.format(branch, head.reference.name, submodule.name))
  subrepo.index.merge_tree(branch)

def MergeAll(repo, branchName):
  for submodule in repo.submodules:
    Merge(submodule, branchName)


def Tag(submodule, tagName, tagDescription):
  print('Creating tag {} in {}'.format(tagName, submodule.name))
  subrepo = submodule.module()
  subrepo.create_tag(path = tagName, message = tagDescription)

def TagAll(repo, tagName, tagDescription):
  for submodule in repo.submodules:
    Tag(submodule, tagName, tagDescription)


def Push(submodule):
  print('Pushing {}'.format(submodule.name))
  subrepo = submodule.module()
  remote = subrepo.remote('origin')
  remote.push()

def PushAll(repo)
  for submodule in repo.submodules:
    PushAll(submodule)
