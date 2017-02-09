import unittest
from spec import skip
import PorousMediaLab
import numpy as np
from scipy import special
# from unittest import TestCase


class TestIntialization:
    """Test the initialization of the PorousMediaLab class with correct boundary conditions  and initial concentrations"""

    def initial_concentrations_test(self):
        """ Scalar initial condition assigned to the whole vector"""
        D = 40
        w = 0.2
        t = 0.1
        dx = 0.1
        L = 1
        phi = 1
        dt = 0.1
        C = PorousMediaLab.PorousMediaLab(L, dx, t, dt, phi, w)
        init_C = 12.32
        C.add_solute_species('O2', D, init_C, init_C)
        print(C.O2.concentration)
        assert np.array_equal(C.O2.concentration[:, 0], init_C * np.ones((L / dx + 1)))

    def boundary_conditions_test(self):
        """ Dirichlet BC at the interface always assigned"""
        D = 40
        w = 0.2
        t = 0.1
        dx = 0.1
        L = 1
        phi = 1
        dt = 0.01
        C = PorousMediaLab.PorousMediaLab(L, dx, t, dt, phi, w)
        init_C = 12.32
        bc = 0.2
        C.add_solute_species('O2', D, init_C, bc)
        print(C.O2.concentration)
        C.solve()
        assert np.array_equal(C.O2.concentration[0, :], bc * np.ones((t / dt + 1)))

class TestMathModel:
    """Testing the accuracy of numerical solutions of integrators"""

    def transport_equation_test(self):
        '''Check the transport equation integrator'''
        D = 40
        w = 0.2
        t = 0.1
        dx = 0.1
        L = 100
        phi = 1
        dt = 0.001
        C = PorousMediaLab.PorousMediaLab(L, dx, t, dt, phi, w)
        C.add_solute_species('O2', D, 0.0, 1)
        C.dcdt.O2 = '0'
        C.solve()
        x = np.linspace(0, L, L / dx + 1)
        sol = 1 / 2 * (special.erfc((x - w * t) / 2 / np.sqrt(D * t)) + np.exp(w * x / D) * special.erfc((x + w * t) / 2 / np.sqrt(D * t)))

        assert max(C.O2.concentration[:, -1] - sol) < 1e-4

    def rk4_ode_solver_test(self):
        """Testing 4th order Runge-Kutta ode solver"""
        # dCdt = -R, where R = kC, has a solution C(t)=C0*exp(-kt)
        # C0 = 1
        # k = 2
        C0 = {'C': 1}
        coef = {'k': 2}
        rates = {'R': 'k*C'}
        dcdt = {'C': '-R'}
        dt = 0.0001
        T = 0.01
        time = np.linspace(0, T, T / dt + 1)
        num_sol = np.array(C0['C'])
        for i in range(1, len(time)):
            C_new, _ = PorousMediaLab.ode_integrate(C0, dcdt, rates, coef, dt, solver=1)
            C0['C'] = C_new['C']
            num_sol = np.append(num_sol, C_new['C'])
        assert max(num_sol - np.exp(-coef['k'] * time)) < 1e-5

    def butcher5_ode_solver_test(self):
        """Testing 5th order Butcher ode solver"""
        # dCdt = -R, where R = kC, has a solution C(t)=C0*exp(-kt)
        # C0 = 1
        # k = 2
        C0 = {'C': 1}
        coef = {'k': 2}
        rates = {'R': 'k*C'}
        dcdt = {'C': '-R'}
        dt = 0.0001
        T = 0.01
        time = np.linspace(0, T, T / dt + 1)
        num_sol = np.array(C0['C'])
        for i in range(1, len(time)):
            C_new, _ = PorousMediaLab.ode_integrate(C0, dcdt, rates, coef, dt, solver=0)
            C0['C'] = C_new['C']
            num_sol = np.append(num_sol, C_new['C'])
        assert max(num_sol - np.exp(-coef['k'] * time)) < 1e-5

    def adjust_time_test(self):
        """adjusting time step"""
        skip()


class TestHandling(unittest.TestCase):
    """Test the exception handling with correct terminal messages"""

    def ode_solver_key_error_test(self):
        """Key error with incorrect rates and dcdt in the ode"""
        C0 = {'C': 1}
        coef = {'k': 2}
        rates = {'R': 'k*C'}
        dcdt = {'C1': '-R'}
        dt = 0.0001
        with self.assertRaises(KeyError):
            PorousMediaLab.ode_integrate(C0, dcdt, rates, coef, dt, solver=0)

    def bc_error_test(self):
        """boundary condition error """
        skip()
