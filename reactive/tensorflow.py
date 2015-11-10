import os

from charmhelpers.core.hookenv import (
    status_set,
    config,
)

from charms.reactive import (
    when,
    when_not,
    hook,
    is_state,
    set_state,
    remove_state,
)

from charmhelpers.fetch import (
    apt_install,
)


def install_cuda():
    pass


def install_tensorflow(version, cuda=False):
    import pip

    if version == 'stable':
        # REFACTOR don't do this
        version = '0.5.0'

    status_set('maintenance', 'installing %s' % version)
    url = 'https://storage.googleapis.com/tensorflow/linux/{type}/tensorflow-{version}-cp27-none-linux_x86_64.whl'
    pip.main(['install',
              url.format(version=version, type='cpu')])
    status_set('maintenance', 'installed')


def install_tensorflow_source():
    pass


def install_deps(source, cuda):
    if is_state('tensorflow.deps-installed'):
        return
    # MAGIC
    if source:
        apt_install(['python-numpy',  'swig', 'python-dev'])

    if cuda:
        install_cuda()

    apt_install(['python-pip', 'python-dev'])
    set_state('tensorflow.deps-installed')


@hook('config-changed')
def configure():
    cfg = config()
    cuda = cfg.get('tensorflow-cuda')
    version = cfg.get('tensorflow-version')

    if version == 'source':
        status_set('blocked', 'Can not install tensorflow from source yet.')
        return

    if cuda:
        status_set('blocked', 'Please dont use me')

    if cfg.changed('tensorflow-cuda') or cfg.changed('version') and is_state('tensorflow.deps-installed'):
        remove_state('tensorflow.deps-installed')

    install_deps(version == 'source', cuda)

    if version == 'source':
        install_tensorflow_source()
    else:
        install_tensorflow(version, cuda)

    set_state('tensorflow.ready')


@hook('upgrade-charm')
def workaround():
    remove_state('tensorflow.deps-installed')
