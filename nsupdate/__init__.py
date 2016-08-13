"""
nsupdate - dynamic DNS service
"""

import re


class Version(tuple):  # pragma: no cover
    """
    Version objects store versions like 1.2.3a4 in a structured
    way and support version comparisons and direct version component access.
    1: major version (digits only)
    2: minor version (digits only)
    3: (maintenance) release version (digits only)
    a4: optional additional version specification (str)

    See PEP386 for more details.
    TODO: use 3rd party code for PEP386 version numbers later.

    You can create a Version instance either by giving the components, like:
        Version(1,2,3,'a4')
    or by giving the composite version string, like:
        Version(version="1.2.3a4").

    Version subclasses tuple, so comparisons to tuples should work.
    Also, we inherit all the comparison logic from tuple base class.
    """
    VERSION_RE = re.compile(
        r"""
        (?P<major>\d+)
        \.
        (?P<minor>\d+)
        \.
        (?P<release>\d+)
        (?P<additional>[abc]\d+)?""",
        re.VERBOSE)

    @classmethod
    def parse_version(cls, version):
        match = cls.VERSION_RE.match(version)
        if match is None:
            raise ValueError("Unexpected version string format: {0!r}".format(version))
        v = match.groupdict()
        return int(v['major']), int(v['minor']), int(v['release']), str(v['additional'] or 'd0')

    def __new__(cls, major=0, minor=0, release=0, additional='d0', version=None):
        # HACK: Use "d0" for release, as "d0" > "c99".
        if version:
            major, minor, release, additional = cls.parse_version(version)
        return tuple.__new__(cls, (major, minor, release, additional))

    # properties for easy access of version components
    major = property(lambda self: self[0])
    minor = property(lambda self: self[1])
    release = property(lambda self: self[2])
    additional = property(lambda self: self[3] if self[3] != 'd0' else '')

    def __str__(self):
        version_str = "{0}.{1}.{2}".format(self.major, self.minor, self.release)
        if self.additional != 'd0':
            version_str += self.additional
        return version_str


version = Version(0, 12, 0)
