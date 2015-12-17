from metaborg.util.eclipse import EclipseGenerator


class MetaborgEclipseGenerator(EclipseGenerator):
  eclipseRepo = 'http://eclipse.mirror.triple-it.nl/releases/mars/'
  eclipseIU = 'epp.package.committers'

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

  spoofaxRepo = 'http://download.spoofax.org/update/nightly/'
  spoofaxRepoLocal = 'spoofax-deploy/org.strategoxt.imp.updatesite/target/site'
  spoofaxIU = 'org.strategoxt.imp.feature.group'
  spoofaxMetaIU = 'org.strategoxt.imp.meta.feature.group'
  modelwareIUs = [
    'org.metaborg.modelware.gmf.feature.group',
    'org.metaborg.modelware.gmf.headless.feature.group',
    'org.metaborg.modelware.emf.feature.group'
  ]
  modelwareMetaIUs = ['org.metaborg.modelware.gmf.meta.feature.group', 'org.metaborg.modelware.emf.meta.feature.group']

  def __init__(self, destination, config, eclipseRepo = None, eclipseIU = None, installSpoofax = True,
               spoofaxRepo = None, spoofaxDevelop = False, spoofaxModelware = False, moreRepos = None, moreIUs = None,
               archive = False):
    if not eclipseRepo:
      eclipseRepo = MetaborgEclipseGenerator.eclipseRepo
    if not eclipseIU:
      eclipseIU = MetaborgEclipseGenerator.eclipseIU
    if not spoofaxRepo:
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

    EclipseGenerator.__init__(self, destination, config, repos, ius, archive)
