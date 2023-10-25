'''
Kalman filter
'''

import numpy as np
import numpy.typing as npt
import cv2 as cv

class Kalman3D:
    '''
    Kalman3D: Kalman filter to track a 3D point (x,y,z)
    All X Y Z should be in meters -- NOT in millimeters
    '''
    ##-#######################################################################################
    ## User-level Properties that can be changed for tuning
    ##-#######################################################################################
    drag: float = 0.0    # Drag felt by all axes (for example, air resistance)
    grav: float = 0.0  # The constant acceleration on Y-axis
    procNoise: float = 0.1    # Process noise -- how good is our model?
    # 0.8: More uncertainty => more weight to prediction  (trust the model more)
    # 0.1: Less uncertainty => more weight to measurement (trust the measurement more)
    measNoise:float = 0.1    # Measurement noise: How good is the tracking?
    ##-#######################################################################################



    ##-#######################################################################################
    ## Properties that don't need to be changed for tuning

    nstates : int = 7 # px, py, pd, vx, vy, vd ay(6x6 matrix)
    nmeasures : int = 3 # All position data (p*), no velocities (v*)
    kf = cv.KalmanFilter(nstates, nmeasures, 0)
    # State variable indices
    SPX:int = 0
    SPY:int = 1
    SPZ:int = 2
    SVX:int = 3
    SVY:int = 4
    SVZ:int = 5
    SAC:int = 6 # the constant acceleration; make sure to initialize it to a constant
    # Measurement variable indices
    MPX:int = 0
    MPY:int = 1
    MPZ:int = 2


    def __init__(self, drag:float = 1.0, debug:int = 0) -> None:
        '''
        Params:
        drag: Drag coefficient. Use this to introduce drag. This is only an approximation
        '''

        self.drag = drag
        self.debug = debug

        self.ticks     = 0     # keep track of time since last update (for dT)
        self.lastTicks = 0     #
        if self.debug >= 2:
            print("nstates", Kalman3D.nstates)

        # A: Transition State Matrix -- the dynamics (constant acceleration model)
        # dT will be updated at each time stamp (could be fixed to; we are not using fixed dT)
        #    [PX   PY   PD   VX   VY   VD  AC  ]
        # px [ 1    0    0   dT    0    0 .5d2 ] (.5d2 --> 0.5 * dT**2)
        # py [ 0    1    0    0   dT    0 .5d2 ]
        # pd [ 0    0    1    0    0   dT .5d2 ]
        # vx [ 0    0    0   Drg   0    0   dT ]
        # vy [ 0    0    0    0   Drg   0   dT ]
        # vd [ 0    0    0    0    0   Drg  dT ]
        # ac [ 0    0    0    0    0    0   1  ]
        Kalman3D.kf.transitionMatrix = np.eye(Kalman3D.nstates, dtype=np.float32)
        Kalman3D.kf.transitionMatrix[Kalman3D.SVX, Kalman3D.SVX] = self.drag
        Kalman3D.kf.transitionMatrix[Kalman3D.SVY, Kalman3D.SVY] = self.drag
        Kalman3D.kf.transitionMatrix[Kalman3D.SVZ, Kalman3D.SVZ] = self.drag
        if self.debug >= 3:
            print("transitionMatrix: shape:{}\n{}".format(Kalman3D.kf.transitionMatrix.shape,
                Kalman3D.kf.transitionMatrix))

        # H: Measurement Matrix
        # [ 1 0 0 0 0 0 0] X
        # [ 0 1 0 0 0 0 0] Y
        # [ 0 0 1 0 0 0 0] D
        Kalman3D.kf.measurementMatrix = np.eye(Kalman3D.nmeasures, Kalman3D.nstates, dtype=np.float32)
        if self.debug >= 3:
            print("measurementMatrix: shape:{}\n{}".format(Kalman3D.kf.measurementMatrix.shape,
                Kalman3D.kf.measurementMatrix))


        # Q: Process Noise Covariance Matrix
        # [ Epx 0   0   0   0   0   0   ]
        # [ 0   Epy 0   0   0   0   0   ]
        # [ 0   0   Epd 0   0   0   0   ]
        # [ 0   0   0   Evx 0   0   0   ]
        # [ 0   0   0   0   Evy 0   0   ]
        # [ 0   0   0   0   0   Evd 0   ]
        # [ 0   0   0   0   0   0   Eac ]
        Kalman3D.kf.processNoiseCov = np.eye(Kalman3D.nstates, dtype=np.float32)*Kalman3D.procNoise
        # Override errors for velocities (rely more on measurement for velocity rather than our model)
        Kalman3D.kf.processNoiseCov[Kalman3D.SVX, Kalman3D.SVX] = 8.0;
        Kalman3D.kf.processNoiseCov[Kalman3D.SVY, Kalman3D.SVY] = 8.0;
        Kalman3D.kf.processNoiseCov[Kalman3D.SVZ, Kalman3D.SVZ] = 8.0;
        if self.debug>=3: print("processNoiseCov: shape:{}\n{}".format(Kalman3D.kf.processNoiseCov.shape,
            Kalman3D.kf.processNoiseCov))

        # R: Measurement Noise Covariance Matrix
        Kalman3D.kf.measurementNoiseCov = np.eye(Kalman3D.nmeasures,
            dtype=np.float32)*Kalman3D.measNoise
        if self.debug >= 3:
            print("measurementNoiseCov: shape:{}\n{}".format(Kalman3D.kf.measurementNoiseCov.shape,
                Kalman3D.kf.measurementNoiseCov))


    ## Public method 1/3
    def init(self, meas: npt.NDArray) -> np.ndarray:
        '''
        Initialize the filter initial state
        Kalman filter actually doesn't have an init method. We just our hack our way through it.
        '''
        state = np.zeros(Kalman3D.kf.statePost.shape, np.float32)
        state[Kalman3D.SPX] = meas[Kalman3D.SPX];
        state[Kalman3D.SPY] = meas[Kalman3D.SPY];
        state[Kalman3D.SPZ] = meas[Kalman3D.SPZ];
        state[Kalman3D.SVX] = 0.1;
        state[Kalman3D.SVY] = 0.1;
        state[Kalman3D.SVZ] = 0.1;
        state[Kalman3D.SAC] = Kalman3D.grav;
        Kalman3D.kf.statePost = state;
        Kalman3D.kf.statePre  = state;
        if self.debug >= 2:
            print("statePost: shape:{}\n{}".format(Kalman3D.kf.statePost.shape, Kalman3D.kf.statePost))

        self.lastTicks = self.ticks;
        self.ticks = cv.getTickCount();
        return meas

    def track(self, meas, dT=-1., onlyPred=False):
        '''
        User level function to do the tracking.
        meas: measurement data (ball position)
        Returns currently predicted (filtered) position of the ball
        '''
        if (onlyPred): ## only predict; ignore meas
            # This will be useful when there are no predictions available or
            # to predict future trajectory based on past measurements
            pred = self.Kpredict(dT)            # get predictions
            cpred = self.Kcorrect(pred, False)  # update with predicted values (restart means used pred value for correction 100% weight)
            if self.debug >= 1:
                print("---------------------------------------------------")
                print("meas current               : None (only predicting)")
                print("pred predicted without meas: {}\n".format(cpred))
        else: # use meas to correct prediction
            pred = self.Kpredict(dT)           # get predictions
            cpred = self.Kcorrect(meas, False) # Kalman correct with measurement
            if self.debug >= 1:
                print("---------------------------------------------------")
                print("meas current               : {}".format(meas))
                print("pred predicted             : {}\n".format(cpred))

        return cpred

    def predict(self, dT=-1.):
        '''
        User level convenience function to do the prediction of trajectory.
        Returns predicted position
        '''
        return self.track(meas=None, dT=dT, onlyPred=True)

    def Kpredict(self, dT=-1.):
        '''
        Get predicted state. Each mat is a 3D point
        '''
        if (dT <= 0):
            self.lastTicks = self.ticks
            self.ticks = cv.getTickCount();
            dT = 1.0 * (self.ticks - self.lastTicks) / cv.getTickFrequency(); ## seconds

        if self.debug >= 2:
            print("dT: {:1.4f}".format(dT))
        # Update the transition Matrix A with dT for this time stamp
        Kalman3D.kf.transitionMatrix[Kalman3D.SPX, Kalman3D.SVX] = dT;
        Kalman3D.kf.transitionMatrix[Kalman3D.SPY, Kalman3D.SVY] = dT;
        Kalman3D.kf.transitionMatrix[Kalman3D.SPZ, Kalman3D.SVZ] = dT;

        #Kalman3D.kf.transitionMatrix[SVX, SAC] = -dT;
        Kalman3D.kf.transitionMatrix[Kalman3D.SVY, Kalman3D.SAC] = -dT;
        #Kalman3D.kf.transitionMatrix[SVZ, SAC] = -dT;
        Kalman3D.kf.transitionMatrix[Kalman3D.SAC, Kalman3D.SAC] = 1.;

        pred = Kalman3D.kf.predict()
        return np.float32([pred[Kalman3D.SPX],
            pred[Kalman3D.SPY],
            pred[Kalman3D.SPZ]]).squeeze()


    def Kcorrect(self, meas, restart=False):
        '''
        State correction using measurement matrix with 3D points
        '''
        if (restart): # Restart the filter
            # Initialization
            cv.setIdentity(Kalman3D.kf.errorCovPre, 1.0);

            # Force the measurement to be used with 100% weight ignoring Hx
            Kalman3D.kf.statePost[Kalman3D.SPX] = meas[Kalman3D.SPX];
            Kalman3D.kf.statePost[Kalman3D.SPY] = meas[Kalman3D.SPY];
            Kalman3D.kf.statePost[Kalman3D.SPZ] = meas[Kalman3D.SPZ];
            Kalman3D.kf.statePost[Kalman3D.SVX] = 3.;
            Kalman3D.kf.statePost[Kalman3D.SVY] = 3.;
            Kalman3D.kf.statePost[Kalman3D.SVZ] = 3.;
            Kalman3D.kf.statePost[Kalman3D.SAC] = Kalman3D.grav;
        else:
            Kalman3D.kf.correct(meas); # Kalman Correction
        return np.float32([Kalman3D.kf.statePost[Kalman3D.SPX],
            Kalman3D.kf.statePost[Kalman3D.SPY],
            Kalman3D.kf.statePost[Kalman3D.SPZ]]).squeeze()


    def getPostState(self):
        '''
        Get the state after correction
        '''
        return np.float32([Kalman3D.kf.statePost[Kalman3D.SPX],
            Kalman3D.kf.statePost[Kalman3D.SPY],
            Kalman3D.kf.statePost[Kalman3D.SPZ]]).squeeze()

