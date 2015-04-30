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

def Branch(repo):
  head = repo.head
  if head.is_detached:
    return "DETACHED"
  return head.reference.name


def Update(repo, submodule, init = False, remote = True, recursive = True, depth = None):
  if not submodule.module_exists():
    init = True

  args = ['update', '--recursive', '--rebase']

  if init:
      args.append('--init')
  if remote:
      args.append('--remote')
  if recursive:
      args.append('--recursive')
  if depth:
    args.append('--depth')
    args.append(depth)

  if init:
    print('Initializing {}'.format(submodule.name))
  else:
    subrepo = submodule.module()
    remote = subrepo.remote('origin')
    head = subrepo.head
    if head.is_detached:
      print('Updating {}'.format(submodule.name))
    else:
      print('Updating {} from {}/{}'.format(submodule.name, remote.name, head.reference.name))

  repo.git.submodule(args, '--', submodule.name)

def UpdateAll(repo, depth = None):
  for submodule in repo.submodules:
    Update(repo, submodule, depth = depth)


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


def Reset(submodule, toRemote):
  subrepo = submodule.module()
  if toRemote:
    head = subrepo.head
    if head.is_detached:
      print('Cannot reset, {} has a DETACHED HEAD.'.format(submodule.name))
      return
    remote = subrepo.remote('origin')
    branchName = '{}/{}'.format(remote.name, head.reference.name)
    print('Resetting {} to {}'.format(submodule.name, branchName))
    subrepo.git.reset('--hard', branchName)
  else:
    print('Resetting {}'.format(submodule.name))
    subrepo.git.reset('--hard')

def ResetAll(repo, toRemote):
  for submodule in repo.submodules:
    Reset(submodule, toRemote)


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


def Push(submodule, **kwargs):
  print('Pushing {}'.format(submodule.name))
  subrepo = submodule.module()
  remote = subrepo.remote('origin')
  remote.push(**kwargs)

def PushAll(repo, **kwargs):
  for submodule in repo.submodules:
    Push(submodule, **kwargs)


def Track(submodule):
  subrepo = submodule.module()
  head = subrepo.head
  remote = subrepo.remote('origin')
  localBranchName = head.reference.name
  remoteBranchName = '{}/{}'.format(remote.name, localBranchName)
  print('Setting tracking branch for {} to {}'.format(localBranchName, remoteBranchName))
  subrepo.git.branch('-u', remoteBranchName, localBranchName)

def TrackAll(repo):
  for submodule in repo.submodules:
    Track(submodule)


def InitAll(repo, depth = None):
  for submodule in repo.submodules:
    Update(repo, submodule, init = True, remote = False, recursive = True, depth = depth)
