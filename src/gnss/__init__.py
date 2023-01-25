class GNSS:
    # Parent class for all GNSS systems

    @property
    def symbol(self) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def obs_types(self) -> [str]:
        raise NotImplementedError

    def __repr__(self):
        return self.name + ": " + str(self.obs_types)


class GPS(GNSS):
    symbol = 'G'

    name = 'GPS'

    obs_types = []


class SBAS(GNSS):
    symbol = 'S'

    name = 'SBAS'

    obs_types = []


class GLO(GNSS):
    symbol = 'R'

    name = 'GLONASS'

    obs_types = []


class GAL(GNSS):
    symbol = 'E'

    name = 'Galileo'

    obs_types = []


class QZS(GNSS):
    symbol = 'J'

    name = 'QZSS'

    obs_types = []


class BDT(GNSS):
    symbol = 'C'

    name = "BeiDou"

    obs_types = []


class IRN(GNSS):
    symbol = 'I'

    name = "IRN"

    obs_types = []


class Mixed(GNSS):
    symbol = 'M'

    name = "Mixed"

    obs_types = []


def get_correct_gnss(name: str) -> GNSS:
    if name == 'G':
        return GPS()
    elif name == 'R':
        return GLO()
    elif name == 'E':
        return GAL()
    elif name == 'J':
        return QZS()
    elif name == 'C':
        return BDT()
    elif name == 'I':
        return IRN()
    elif name == 'S':
        return SBAS()
    elif name == 'M':
        return Mixed()
    else:
        raise ValueError("Unknown GNSS system: " + name)
