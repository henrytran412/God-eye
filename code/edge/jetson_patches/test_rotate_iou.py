"""Correctness tests for the CPU rotated-IoU replacement."""
import sys, math
import numpy as np
sys.path.insert(0, "/home/sjsujetson/godeye")
from rotate_iou_cpu import rotate_iou_gpu_eval as iou

def close(a, b, tol=1e-4): return abs(a - b) < tol

# 1. identical boxes -> IoU 1
a = np.array([[0., 0., 2., 4., 0.]])
assert close(iou(a, a)[0, 0], 1.0), iou(a, a)
print("  identical                 OK  1.0")

# 2. disjoint -> 0
b = np.array([[100., 100., 2., 4., 0.]])
assert close(iou(a, b)[0, 0], 0.0)
print("  disjoint                  OK  0.0")

# 3. axis-aligned half overlap: two 2x2 squares offset by 1 in x
#    inter = 1*2 = 2, union = 4+4-2 = 6 -> 1/3
s1 = np.array([[0., 0., 2., 2., 0.]]); s2 = np.array([[1., 0., 2., 2., 0.]])
assert close(iou(s1, s2)[0, 0], 1.0/3.0), iou(s1, s2)
print("  half overlap              OK  0.3333")

# 4. 90-degree rotation of a square is the same square -> IoU 1
r = np.array([[0., 0., 2., 2., math.pi/2]])
assert close(iou(s1, r)[0, 0], 1.0), iou(s1, r)
print("  square rotated 90 deg     OK  1.0")

# 5. rotating a 2x4 rect by 90 deg gives a 4x2 rect: inter = 2*2 = 4,
#    union = 8 + 8 - 4 = 12 -> 1/3
q1 = np.array([[0., 0., 2., 4., 0.]]); q2 = np.array([[0., 0., 2., 4., math.pi/2]])
assert close(iou(q1, q2)[0, 0], 1.0/3.0), iou(q1, q2)
print("  rect rotated 90 deg       OK  0.3333")

# 6. criterion semantics: small box fully inside a big one
sm = np.array([[0., 0., 1., 1., 0.]]); bg = np.array([[0., 0., 4., 4., 0.]])
assert close(iou(sm, bg, -1)[0, 0], 1.0/16.0)     # 1 / (1+16-1)
assert close(iou(sm, bg, 0)[0, 0], 1.0)           # inter / area(small)
assert close(iou(sm, bg, 1)[0, 0], 1.0/16.0)      # inter / area(big)
assert close(iou(sm, bg, 2)[0, 0], 1.0)           # raw intersection AREA
print("  criterion -1/0/1/2        OK")

# 7. rotation direction is clockwise: a wide box rotated +45 deg must have its
#    first corner where the CUDA kernel would put it
c = np.array([[0., 0., 2., 0.0001, math.pi/4]])
from rotate_iou_cpu import _corners
xy = _corners(c)[0]
assert xy[3][0] > 0 and xy[3][1] < 0, xy   # +x local -> (+,-) under clockwise
print("  clockwise convention      OK")

# 8. shape and dtype
m = iou(np.random.rand(7, 5) * 10, np.random.rand(3, 5) * 10)
assert m.shape == (7, 3) and m.dtype == np.float32
print("  shape/dtype               OK  (7,3) float32")
print("ALL ROTATE_IOU TESTS PASSED")
