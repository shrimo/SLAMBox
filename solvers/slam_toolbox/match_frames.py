import cv2
import numpy as np
np.set_printoptions(suppress=True)
from skimage.measure import ransac # type: ignore
from skimage.transform import FundamentalMatrixTransform # type: ignore
from skimage.transform import EssentialMatrixTransform # type: ignore

def poseRt(R, t):
    ret = np.eye(4)
    ret[:3, :3] = R
    ret[:3, 3] = t
    return ret

# pose
def fundamentalToRt(F):
    W = np.mat([[0,-1,0],[1,0,0],[0,0,1]], dtype=float)
    U,d,Vt = np.linalg.svd(F)
    if np.linalg.det(U) < 0:
        U *= -1.0
    if np.linalg.det(Vt) < 0:
        Vt *= -1.0
    R = U @ W @ Vt
    if np.sum(R.diagonal()) < 0:
        R = U @ W.T @ Vt
    t = U[:, 2]

    # TODO: Resolve ambiguities in better ways. This is wrong.
    if t[2] < 0:
        t *= -1

    # # TODO: UGLY!
    # if os.getenv("REVERSE") is not None:
    #     t *= -1
    return np.linalg.inv(poseRt(R, t))

bf = cv2.BFMatcher(cv2.NORM_HAMMING)
def match_frame(f1, f2, m_samples=8, r_threshold=0.01, m_trials=300):
    matches = bf.knnMatch(f1.descriptors, f2.descriptors, k=2)

    # Lowe's ratio test
    ret = []
    idx1, idx2 = [], []
    idx1s, idx2s = set(), set()
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            p1 = f1.kps[m.queryIdx]
            p2 = f2.kps[m.trainIdx]
            # be within orb distance 32
            if m.distance < 32:
                # keep around indices
                # TODO: refactor this to not be O(N^2)
                if m.queryIdx not in idx1s and m.trainIdx not in idx2s:
                    idx1.append(m.queryIdx)
                    idx2.append(m.trainIdx)
                    idx1s.add(m.queryIdx)
                    idx2s.add(m.trainIdx)
                    ret.append((p1, p2))

    # no duplicates
    assert(len(set(idx1)) == len(idx1))
    assert(len(set(idx2)) == len(idx2))

    assert len(ret) >= 8
    ret = np.array(ret)
    idx1 = np.array(idx1)
    idx2 = np.array(idx2)

    # fit matrix
    model, inliers = ransac((ret[:, 0], ret[:, 1]),
                            EssentialMatrixTransform,
                            min_samples=m_samples,
                            residual_threshold=r_threshold,
                            max_trials=m_trials)
    # print("Matches:  %d -> %d -> %d -> %d" % (len(f1.descriptors), len(matches), len(inliers), sum(inliers)))
    return idx1[inliers], idx2[inliers], fundamentalToRt(model.params)

