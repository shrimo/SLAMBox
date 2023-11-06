import numpy as np
import cv2 as cv


class Kalman3D:
    def __init__(self, drag=1.0, debug=False, grav=0.0, procNoise=0.1, measNoise=0.1):
        self.drag = drag
        self.debug = debug
        self.ticks = 0
        self.lastTicks = 0
        self.grav = grav
        self.procNoise = procNoise
        self.measNoise = measNoise
        self.setup_kalman_filter()
        self.setup_transition_matrix()
        self.setup_measurement_matrix()
        self.setup_process_noise_covariance()
        self.setup_measurement_noise_covariance()

    def setup_kalman_filter(self):
        self.nstates = 7
        self.nmeasures = 3
        self.kf = cv.KalmanFilter(self.nstates, self.nmeasures, 0)

    def setup_transition_matrix(self):
        self.SPX, self.SPY, self.SPZ, self.SVX, self.SVY, self.SVZ, self.SAC = (
            0,
            1,
            2,
            3,
            4,
            5,
            6,
        )
        self.kf.transitionMatrix = np.eye(self.nstates, dtype=np.float32)
        self.kf.transitionMatrix[self.SVX, self.SVX] = self.drag
        self.kf.transitionMatrix[self.SVY, self.SVY] = self.drag
        self.kf.transitionMatrix[self.SVZ, self.SVZ] = self.drag

    def setup_measurement_matrix(self):
        self.MPX, self.MPY, self.MPZ = 0, 1, 2
        self.kf.measurementMatrix = np.eye(
            self.nmeasures, self.nstates, dtype=np.float32
        )

    def setup_process_noise_covariance(self):
        self.kf.processNoiseCov = (
            np.eye(self.nstates, dtype=np.float32) * self.procNoise
        )
        self.kf.processNoiseCov[self.SVX, self.SVX] = 8.0
        self.kf.processNoiseCov[self.SVY, self.SVY] = 8.0
        self.kf.processNoiseCov[self.SVZ, self.SVZ] = 8.0

    def setup_measurement_noise_covariance(self):
        self.kf.measurementNoiseCov = (
            np.eye(self.nmeasures, dtype=np.float32) * self.measNoise
        )

    def init(self, meas=np.float32([0, 0, 0])):
        state = np.zeros(self.kf.statePost.shape, np.float32)
        state[self.SPX] = meas[self.SPX]
        state[self.SPY] = meas[self.SPY]
        state[self.SPZ] = meas[self.SPZ]
        state[self.SVX] = 0.1
        state[self.SVY] = 0.1
        state[self.SVZ] = 0.1
        state[self.SAC] = self.grav
        self.kf.statePost = state
        self.kf.statePre = state
        self.lastTicks = self.ticks
        self.ticks = cv.getTickCount()
        return meas

    def track(self, meas, dT=-1.0, onlyPred=False):
        if onlyPred:
            pred = self.kpredict(dT)
            cpred = self.kcorrect(pred, False)
            if self.debug:
                print("-" * 51)
                print("meas current               : None (only predicting)")
                print(f"pred predicted without meas: {cpred}\n")
        else:
            pred = self.kpredict(dT)
            cpred = self.kcorrect(meas, False)
            if self.debug:
                print("-" * 51)
                print(f"meas current               : {meas}")
                print(f"pred predicted             : {cpred}\n")
        return cpred

    def predict(self, dT=-1.0):
        return self.track(meas=None, dT=dT, onlyPred=True)

    def kpredict(self, dT=-1.0):
        if dT <= 0:
            self.lastTicks = self.ticks
            self.ticks = cv.getTickCount()
            dT = 1.0 * (self.ticks - self.lastTicks) / cv.getTickFrequency()
        self.kf.transitionMatrix[self.SPX, self.SVX] = dT
        self.kf.transitionMatrix[self.SPY, self.SVY] = dT
        self.kf.transitionMatrix[self.SPZ, self.SVZ] = dT
        self.kf.transitionMatrix[self.SVY, self.SAC] = -dT
        self.kf.transitionMatrix[self.SAC, self.SAC] = 1.0
        pred = self.kf.predict()
        return np.float32([pred[self.SPX], pred[self.SPY], pred[self.SPZ]]).squeeze()

    def kcorrect(self, meas, restart=False):
        if restart:
            cv.setIdentity(self.kf.errorCovPre, 1.0)
            self.kf.statePost[self.SPX] = meas[self.SPX]
            self.kf.statePost[self.SPY] = meas[self.SPY]
            self.kf.statePost[self.SPZ] = meas[self.SPZ]
            self.kf.statePost[self.SVX] = 3.0
            self.kf.statePost[self.SVY] = 3.0
            self.kf.statePost[self.SVZ] = 3.0
            self.kf.statePost[self.SAC] = self.grav
        else:
            self.kf.correct(meas)
        return np.float32(
            [
                self.kf.statePost[self.SPX],
                self.kf.statePost[self.SPY],
                self.kf.statePost[self.SPZ],
            ]
        ).squeeze()

    def getPostState(self):
        return np.float32(
            [
                self.kf.statePost[self.SPX],
                self.kf.statePost[self.SPY],
                self.kf.statePost[self.SPZ],
            ]
        ).squeeze()
