# noinspection PyPep8Naming
def classFactory(iface):
    """Load the ATAQ Plugin class from our main file."""
    from .ataq_plugin import AtaqPlugin
    return AtaqPlugin(iface)
