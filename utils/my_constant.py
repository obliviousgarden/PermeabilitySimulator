from enum import Enum

from scipy import constants


class UnitType(Enum):
    SI = 1
    CGS = 2


class Constant:
    unit_type = UnitType.SI

    def __init__(self, *args):
        if len(args) == 4:
            self.name, self.symbol, self.si_value, self.si_unit = args
            self.convert_factor = 1.
            self.cgs_value = self.si_value
            self.cgs_unit = self.si_unit
        elif len(args) == 6:
            self.name, self.symbol, self.si_value, self.si_unit, self.convert_factor, self.cgs_unit = args
            self.cgs_value = self.si_value * self.convert_factor
        else:
            raise Exception("Incorrect number of arguments")

    @classmethod
    def use(cls, unit_type: UnitType):
        cls.unit_type = unit_type

    def si(self):
        return self.si_value

    def cgs(self):
        return self.cgs_value

    def val(self):
        if self.unit_type == UnitType.SI:
            return self.si()
        else:
            return self.cgs()

    def factor(self):
        return self.convert_factor

    def __str__(self):
        return f'{self.name},{self.symbol}={self.si_value}[{self.si_unit}]={self.cgs_value}[{self.cgs_unit}]'


class ConstantSet:
    unit_type = UnitType.SI

    def __init__(self):
        self._parameters = {}

    @classmethod
    def use(cls, unit_type: UnitType):
        cls.unit_type = unit_type

    def info(self):
        for constant in self._parameters.values():
            print(constant)

    def __getattr__(self, name):
        if name in self._parameters:
            if ConstantSet.unit_type == UnitType.SI:
                return self._parameters[name].si()
            elif ConstantSet.unit_type == UnitType.CGS:
                return self._parameters[name].cgs()
            else:
                raise ValueError("Unsupported unit type")
        else:
            raise AttributeError(f"'ParameterContainer' object has no attribute '{name}'")


pi = Constant("PI", "π", constants.pi, "1", 1., "1")
c = Constant("Speed of light", "c", constants.c, "m/s", 1e2, "cm/s")
e = Constant("Elemental charge", "e", constants.e, "C", constants.c / 10, "statC")
m_e = Constant("Electron mass", "m_e", constants.m_e, "kg", 1e3, "g")
g_e = Constant("Electron's g-factor", "g_e", -2.00231930436118, "1")
h = Constant("Planck constant", "h", constants.h, "J*s", 1e7, "erg*s")
hbar = Constant("Reduced Planck constant", "ħ", constants.hbar, "J*s", 1e7, "erg*s")
miu_0 = Constant("Vacuum permeability", "μ_0", constants.mu_0, "H/m", 10000000 / (4 * constants.pi), "1")
miu_b = Constant("Bohr magneton", "μ_B", e.si() * hbar.si() / (2 * m_e.si()), "J/T",
                 e.factor() * hbar.factor() / m_e.factor() * 1 / c.si(), "erg/G")
gamma_e = Constant("Electron's gyromagnetic ratio", "γ_e", g_e.si() * miu_b.si() / hbar.si(), "Hz/T",
                   g_e.factor() * miu_b.factor() / hbar.factor(), "Hz/G")
gamma = Constant("Electron's gyromagnetic ratio(for LLG)", "γ", - miu_0.si() * g_e.si() * miu_b.si() / hbar.si(), "Hz/(A/m)",
                   1000./(4.*constants.pi), "Hz/Oe")

constants_for_llg = ConstantSet()
constants_for_llg._parameters = {'pi': pi,
                                 'c': c,
                                 'e': e,
                                 'm_e': m_e,
                                 'g_e': g_e,
                                 'h': h,
                                 'hbar': hbar,
                                 'miu_b': miu_b,
                                 'gamma': gamma,
                                 'miu_0': miu_0}

# gamma_e = Constant("Electron's gyromagnetic ratio", "γ", constants., "J*s",1e7, "erg*s")
if __name__ == "__main__":
    constants_for_llg.use(UnitType.CGS)
    print(constants_for_llg.gamma)
    # print(gamma_e)
    # print(miu_0)
