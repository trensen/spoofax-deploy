from metaborg.util.eclipse import EclipseGenerator


class MetaborgEclipseGenerator(EclipseGenerator):
  eclipseRepo = 'http://eclipse.mirror.triple-it.nl/releases/mars/'
  eclipseIU = 'epp.package.java'

  m2eRepos = [
    'http://download.eclipse.org/technology/m2e/releases',
    'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-buildhelper/0.15.0/N/0.15.0.201405280027/',
    'http://download.jboss.org/jbosstools/updates/m2e-extensions/m2e-jdt-compiler/',
    'http://repo1.maven.org/maven2/.m2e/connectors/m2eclipse-tycho/0.7.0/N/LATEST/'
  ]
  m2eIUs = [
    'org.eclipse.m2e.feature.feature.group',
    'org.sonatype.m2e.buildhelper.feature.feature.group',
    'org.jboss.tools.m2e.jdt.feature.feature.group',
    'org.sonatype.tycho.m2e.feature.feature.group'
  ]

  spoofaxRepo = 'http://download.spoofax.org/update/newplugin-nightly/'
  spoofaxRepoLocal = 'spoofax-eclipse/org.metaborg.spoofax.eclipse.updatesite/target/site'
  spoofaxIU = 'org.metaborg.spoofax.eclipse.feature.feature.group'
  spoofaxMetaIU = 'org.metaborg.spoofax.eclipse.meta.feature.feature.group'
  modelwareIUs = []
  modelwareMetaIUs = []

  def __init__(self, workingDir, destination, config, eclipseRepo = None, eclipseIU = None, installSpoofax = True,
               spoofaxRepo = None, spoofaxRepoLocal = False, spoofaxDevelop = False, spoofaxModelware = False,
               moreRepos = None, moreIUs = None, archive = False):
    if not eclipseRepo:
      eclipseRepo = MetaborgEclipseGenerator.eclipseRepo
    if not eclipseIU:
      eclipseIU = MetaborgEclipseGenerator.eclipseIU

    if spoofaxRepoLocal:
      spoofaxRepo = MetaborgEclipseGenerator.spoofaxRepoLocal
    elif not spoofaxRepo:
      spoofaxRepo = MetaborgEclipseGenerator.spoofaxRepo

    if not moreRepos:
      moreRepos = []
    if not moreIUs:
      moreIUs = []

    repos = [eclipseRepo] + MetaborgEclipseGenerator.m2eRepos
    ius = [eclipseIU] + MetaborgEclipseGenerator.m2eIUs

    if installSpoofax:
      repos.append(spoofaxRepo)
      ius.append(MetaborgEclipseGenerator.spoofaxIU)
      if spoofaxDevelop:
        ius.append(MetaborgEclipseGenerator.spoofaxMetaIU)
      if spoofaxModelware:
        ius.extend(MetaborgEclipseGenerator.modelwareIUs)
        if spoofaxDevelop:
          ius.extend(MetaborgEclipseGenerator.modelwareIUs)

    repos.extend(moreRepos)
    ius.extend(moreIUs)

    EclipseGenerator.__init__(self, workingDir, destination, config, repos, ius, archive)
