# 这个文件是根据 山田 的 《磁性材料》编写的
from typing import Union, List, Tuple
from enum import Enum
import numpy as np
import sympy as sy
# np.set_printoptions(precision=32)
from utils.science_plot import SciencePlot, SciencePlotData
from utils.my_constant import constants_for_llg,UnitType


class CGSSampleInfo:
    def __init__(self, Ms: float, Hk: float, rho: float, t: float):
        self.Ms: float = Ms / 10.  # kG->T
        self.Hk: float = Hk * 1000./(4*constants_for_llg.pi)  # Oe->A/m
        self.rho: float = rho * 1e-8  # μΩ*cm->Ω*m
        self.t: float = t * 1e-9  # nm->m
        print(f"New CGS Sample Info:"
              f"\nMs\t={Ms}[kG]\t={self.Ms}[T],"
              f"\nHk\t={Hk}[Oe]\t={self.Hk}[A/m],"
              f"\nρ\t={rho}[μΩ*cm]\t={self.rho}[Ω*m],"
              f"\nt\t={t}[nm]\t={self.t}[m].")

    def get_info(self):
        return self.Ms, self.Hk, self.rho, self.t

class CalculatorType(Enum):
    WANG = 1
    SHIMADA = 2

class LandauLifshitzGilbertCalculator:

    def __init__(self, calculator_type: CalculatorType, unit_type: UnitType, alpha: float,
                 He: float, phi_0: float, delta: float, beta: float):
        self.calculator_type = calculator_type
        self.unit_type = unit_type
        constants_for_llg.use(unit_type)
        constants_for_llg.info()
        self.alpha = alpha  # 衰减常数
        self.Ms = None  # 饱和磁化
        self.Hk = None  # 膝点
        self.He = He  # 外部直流磁场
        self.phi_0 = phi_0  # M在xy平面的投影和e.a.的夹角
        self.delta = delta  # He和e.a.的夹角
        self.beta = beta  # 高频磁场h和e.a.的夹角

        self.freq = None
        self.omega = None
        self.rho = None  # 电导率
        self.t = None  # 膜厚
        print(f"alpha: {self.alpha},He: {self.He},phi_0: {self.phi_0},delta: {self.delta},beta: {self.beta}")

    def calculate(self, f_info: Tuple[float, float], num_points: int, sample_info: CGSSampleInfo):
        min_f, max_f = f_info
        self.freq = np.logspace(np.log10(min_f), np.log10(max_f), num=num_points)
        self.omega = 2 * np.pi * self.freq
        # print(self.freq,self.omega)
        if self.calculator_type == CalculatorType.SHIMADA:
            self.Ms, self.Hk, self.rho, self.t = sample_info.get_info()
            if self.rho == 0.:
                return self.freq, self._miu_shimada()
            else:
                return self.freq, self._miu_shimada_eddy()
        elif self.calculator_type == CalculatorType.WANG:
            pass
        else:
            raise TypeError(f"Unknown calculator type: {self.calculator_type}")
    def _miu_shimada(self):
        # M_S/(μ_0*H_k)
        term_1 = self.Ms/(constants_for_llg.miu_0*self.Hk)
        # ω_r^2 = γ^2*H_k*(H_k+M_S/μ_0)
        omega_r_square = constants_for_llg.gamma**2*self.Hk*(self.Hk+self.Ms/constants_for_llg.miu_0)
        # λ' = (M_S*α*γ)/μ_0
        lambda_prime = self.Ms*self.alpha*constants_for_llg.gamma/constants_for_llg.miu_0
        # ω_r^2-ω^2
        term_2_top_1 = omega_r_square - np.square(self.omega)
        # λ'*ω
        term_2_top_2 = lambda_prime*self.omega
        term_2_bot = np.square(term_2_top_1) + np.square(term_2_top_2)
        rst_real = term_1*omega_r_square*term_2_top_1/term_2_bot+1
        rst_imag = term_1*omega_r_square*term_2_top_2/term_2_bot
        return rst_real,rst_imag

    def _miu_shimada_eddy(self):
        miu_r_real, miu_r_imag = self._miu_shimada()
        # k = t√(ωρ)
        k = self.t*np.sqrt(self.omega/self.rho)
        # μ_r = μ_√(μ_r1^2+μ_r2^2)
        miu_r = np.sqrt(np.square(miu_r_real)+np.square(miu_r_imag))
        # A = √(μ_0/2*(μ_r2+μ_r))
        A = np.sqrt(0.5*constants_for_llg.miu_0*(miu_r_imag+miu_r))
        # B = √(μ_0/2*(-μ_r2+μ_r))
        B = np.sqrt(0.5*constants_for_llg.miu_0*(-miu_r_imag+miu_r))
        # S = k/2*μ_0*μ_r*[cosh(kA)+cos(kB)]
        S = 0.5*k*constants_for_llg.miu_0*miu_r*(np.cosh(k*A)+np.cos(k*B))
        # A*sinh(kA)+B*sinh(kB)
        term_top_1 = A * np.sinh(k * A) + B * np.sinh(k * B)
        # A*sinh(kA)-B*sinh(kB)
        term_top_2 = B * np.sinh(k * A) - A * np.sinh(k * B)
        #
        rst_real = (miu_r_real*term_top_1 - miu_r_imag*term_top_2)/S
        rst_imag = (miu_r_imag*term_top_1 + miu_r_real*term_top_2)/S
        return rst_real, rst_imag




if __name__ == '__main__':
    sample_list_1 = [CGSSampleInfo(15.0, 1, 0, 20000),
                     CGSSampleInfo(15.0, 1, 1500, 20000)]
    sample_list_2 = [CGSSampleInfo(8.0, 0.05, 150, 0.03),
                     CGSSampleInfo(15.0, 0.2, 150, 0.03),
                     CGSSampleInfo(15.0, 0.1, 200, 0.03),
                     CGSSampleInfo(15.0, 0.1, 300, 0.03)]
    sample_list_3 = [CGSSampleInfo(8.0, 0.1, 5, 0.1),
                     CGSSampleInfo(8.0, 0.1, 50, 0.1),
                     CGSSampleInfo(8.0, 0.1, 500, 0.1),
                     CGSSampleInfo(8.0, 0.1, 5000, 0.1),
                     CGSSampleInfo(8.0, 0.1, 50000, 0.1)]
    # sample_list_3 = [OhnumaSampleInfo(8.0, 0.1, 50, 1.0),
    #                  OhnumaSampleInfo(8.0, 0.1, 50, 0.1),
    #                  OhnumaSampleInfo(8.0, 0.1, 50, 0.01),
    #                  OhnumaSampleInfo(8.0, 0.1, 50, 0.001),
    #                  OhnumaSampleInfo(8.0, 0.1, 50, 0.0001)]
    calculator_type: CalculatorType = CalculatorType.SHIMADA
    unit_type: UnitType = UnitType.SI
    alpha: float = 0.001
    # Ms: float = 8.0e3 / 10000  # G->T
    # Hk: float = 0.05 * 1000 / (4 * np.pi)  # Oe->A/m
    # Ku: float = 0.5 * Ms * Hk
    # print("Ku", Ku)
    He: float = 0.
    phi_0: float = 0.
    delta: float = 0.
    beta: float = np.pi / 2

    calculator = LandauLifshitzGilbertCalculator(calculator_type=calculator_type,
                                                 unit_type=unit_type,
                                                 alpha=alpha,
                                                 He=He,
                                                 phi_0=phi_0,
                                                 delta=delta,
                                                 beta=beta)
    f_info = (1., 1e9)
    num_points = 400
    # pho = 150.  # μΩ*cm
    # sigma = 1 / (150. * 1e-8)  # 1/(Ω*m)
    # thickness = 0.03 / 1000  # mm->m
    science_plot_data_1 = SciencePlotData()
    science_plot_data_1.add_figure_info(figure_title="miu-f-REAL", x_label="LOG(frequency)", y_label="miu_real")
    science_plot_data_1.add_figure_info(figure_title="miu-f-IMAG", x_label="LOG(frequency)", y_label="miu_imag")
    index = 1
    for sample_info in sample_list_1:
        freq, (miu_real, miu_imag) = calculator.calculate(f_info=f_info, num_points=num_points, sample_info=sample_info)
        science_plot_data_1.add_plot_data(figure_title="miu-f-REAL", x_data=np.log10(freq), y_data=np.log10(miu_real),
                                          y_legend=f"real_y-{index}")
        science_plot_data_1.add_plot_data(figure_title="miu-f-IMAG", x_data=np.log10(freq), y_data=np.log10(miu_imag),
                                          y_legend=f"imag_y-{index}")
        index += 1

    # science_plot_data_2 = SciencePlotData()
    # science_plot_data_2.add_figure_info(figure_title="miu-f-REAL", x_label="LOG(frequency)", y_label="miu_real")
    # science_plot_data_2.add_figure_info(figure_title="miu-f-IMAG", x_label="LOG(frequency)", y_label="miu_imag")
    # index = 1
    # for sample_info in sample_list_2:
    #     freq, (miu_real, miu_imag) = calculator.calculate(f_info=f_info, num_points=num_points, sample_info=sample_info)
    #     science_plot_data_2.add_plot_data(figure_title="miu-f-REAL", x_data=np.log10(freq), y_data=np.log10(miu_real),
    #                                       y_legend=f"real_y-{index}")
    #     science_plot_data_2.add_plot_data(figure_title="miu-f-IMAG", x_data=np.log10(freq), y_data=np.log10(miu_imag),
    #                                       y_legend=f"imag_y-{index}")
    #     index += 1
    # science_plot_data_3 = SciencePlotData()
    # science_plot_data_3.add_figure_info(figure_title="miu-f-REAL", x_label="LOG(frequency)", y_label="miu_real")
    # science_plot_data_3.add_figure_info(figure_title="miu-f-IMAG", x_label="LOG(frequency)", y_label="miu_imag")
    # index = 1
    # for sample_info in sample_list_3:
    #     freq, (miu_real, miu_imag) = calculator.calculate(f_info=f_info, num_points=num_points, sample_info=sample_info)
    #     science_plot_data_3.add_plot_data(figure_title="miu-f-REAL", x_data=np.log10(freq), y_data=np.log10(miu_real),
    #                                       y_legend=f"real_y-{index}")
    #     science_plot_data_3.add_plot_data(figure_title="miu-f-IMAG", x_data=np.log10(freq), y_data=np.log10(miu_imag),
    #                                       y_legend=f"imag_y-{index}")
    #     index += 1

    SciencePlot.sci_plot(science_plot_data_1)
    # SciencePlot.sci_plot(science_plot_data_2)
    # SciencePlot.sci_plot(science_plot_data_3)
