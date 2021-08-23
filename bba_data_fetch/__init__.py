"""
Version corresponding to the git version tag
"""
from pkg_resources import get_distribution, DistributionNotFound
from bluebrainatlas_datafetch import __name__

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
