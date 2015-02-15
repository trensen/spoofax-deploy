def YesNo(message = None):
  if message != None:
    print(message + ' [Y/n]')
  else:
    print('[Y/n]')
  choice = input()
  if choice != 'Y':
    return False
  return True

def YesNoTwice():
  if YesNo():
    return YesNo("Are you really really sure?")
  return False
