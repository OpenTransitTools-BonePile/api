# this is needed because other parts of the 'ott' package exist in other
# locations, without this statement python will look for the subpackages
# here, won't find them and will throw an error, read more here:
# http://stackoverflow.com/questions/1675734

from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
