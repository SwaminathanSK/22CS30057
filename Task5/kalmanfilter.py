from math import log, exp, sqrt
import sys
import warnings
import numpy as np
from numpy import dot, zeros, eye, isscalar, shape
import numpy.linalg as linalg

class KalmanFilter():

    def __init__(self, dim_x, dim_z, dim_u=0):

        self.dim_x = dim_x
        self.dim_z = dim_z
        self.dim_u = dim_u

        self.x = np.zeros((dim_x, 1))  # state
        self.P = np.eye(dim_x)  # uncertainty covariance
        self.Q = np.eye(dim_x)  # process uncertainty
        self.B = None  # control transition matrix
        self.F = np.eye(dim_x)  # state transition matrix
        self.H = np.zeros((dim_z, dim_x))  # Measurement function
        self.R = np.eye(dim_z)  # state uncertainty
        self._alpha_sq = 1.  # fading memory control
        self.M = np.zeros((dim_z, dim_z))  # process-measurement cross correlation
        self.z = np.array([[None] * self.dim_z]).T

        self.K = mp.zeros((dim_x, dim_z))  # kalman gain
        self.e = np.zeros((dim_z, 1))
        self.S = np.zeros((dim_z, dim_z))  # system uncertainty
        self.SI = np.zeros((dim_z, dim_z))  # inverse system uncertainty

        # identity matrix
        self._I = np.eye(dim_x)

        # these will always be a copy of x,P after predict() is called
        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()

        # these will always be a copy of x,P after update() is called
        self.x_post = self.x.copy()
        self.P_post = self.P.copy()

        self.inv = np.linalg.inv

    def predict(self, u=None, B=None, F=None, Q=None):

        if B is None:
            B = self.B
        if F is None:
            F = self.F
        if Q is None:
            Q = self.Q

        if B is not None and u is not None:
            self.x = np.dot(F, self.x) + np.dot(B, u)
        else:
            self.x = np.dot(F, self.x)

        self.P = np.dot((np.dot(F, self.P)), F.T) + Q

        self.x_prior = self.x.copy()
        self.P_prior = self.P.copy()

        return (self.x_prior, self.P_prior)

    def update(self, z, R=None, H=None):

        if R is None:
            R = self.R
        if H is None:
            H = self.H

        self.e = z - dot(H, self.x)
        self.S = np.dot(np.dot(H, self.P), H.T) + R

        self.SI = self.inv(self.S)
        self.K = np.dot(np.dot(self.P, H.T), self.SI)

        self.x = self.x + np.dot(self.K, self.e)

        IminusKH = self._I - np.dot(K, H)

        self.P = np.dot(np.dot(IminusKH, self.P), IminusKH.T) + np.dot(np.dot(self.K, R), self.K.T)

        self.x_post = self.x.copy()
        self.P_post = self.P.copy()

        return (self.x_post, self.P_post)

