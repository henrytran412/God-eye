"""CPU replacement for evaluators.kitti_utils.rotate_iou.rotate_iou_gpu_eval.

Why: numba's CUDA backend segfaults on this board. A trivial 64-element
@cuda.jit kernel exits 139 (verified), so it is not a bevfusion problem --
numba 0.60 cannot launch kernels on this JetPack 7 / CUDA 12.6 / sm_87 setup.
rotate_iou_gpu_eval is CUDA-only with no CPU path, which takes the whole KITTI
evaluator down with it.

This reproduces the original semantics exactly:

  box = [center_x, center_y, x_dim, y_dim, angle], angle clockwise-positive
  corners_x = [-w/2, -w/2, +w/2, +w/2]
  corners_y = [-h/2, +h/2, +h/2, -h/2]
  x' =  cos*cx + sin*cy + center_x
  y' = -sin*cx + cos*cy + center_y      # i.e. [[cos, sin], [-sin, cos]]

  criterion == -1 -> inter / (area1 + area2 - inter)
  criterion ==  0 -> inter / area1
  criterion ==  1 -> inter / area2
  otherwise       -> inter               (raw area; d3_box_overlap passes 2
                                          and multiplies by a height overlap)

Shapely 2.x is used for the polygon intersection because its operations are
vectorised in C; an axis-aligned bounding-box prefilter skips the pairs that
cannot overlap, which is the large majority.
"""
import numpy as np
import shapely


def _corners(boxes: np.ndarray) -> np.ndarray:
    """(N,5) boxes -> (N,4,2) corner coordinates, matching the CUDA kernel."""
    cx, cy, xd, yd, ang = (boxes[:, i] for i in range(5))
    lx = np.stack([-xd / 2, -xd / 2, xd / 2, xd / 2], axis=1)   # (N,4)
    ly = np.stack([-yd / 2, yd / 2, yd / 2, -yd / 2], axis=1)
    c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
    x = c * lx + s * ly + cx[:, None]
    y = -s * lx + c * ly + cy[:, None]
    return np.stack([x, y], axis=2)                              # (N,4,2)


def rotate_iou_gpu_eval(boxes, query_boxes, criterion=-1, device_id=0):
    boxes = np.ascontiguousarray(boxes, dtype=np.float64)
    query_boxes = np.ascontiguousarray(query_boxes, dtype=np.float64)
    N, K = boxes.shape[0], query_boxes.shape[0]
    out = np.zeros((N, K), dtype=np.float32)
    if N == 0 or K == 0:
        return out

    cb, cq = _corners(boxes), _corners(query_boxes)
    pb = shapely.polygons(cb)
    pq = shapely.polygons(cq)

    # AABB prefilter: only pairs whose axis-aligned bounds overlap can intersect
    bb = np.stack([cb[:, :, 0].min(1), cb[:, :, 1].min(1),
                   cb[:, :, 0].max(1), cb[:, :, 1].max(1)], axis=1)
    bq = np.stack([cq[:, :, 0].min(1), cq[:, :, 1].min(1),
                   cq[:, :, 0].max(1), cq[:, :, 1].max(1)], axis=1)
    cand = ((bb[:, None, 0] < bq[None, :, 2]) & (bb[:, None, 2] > bq[None, :, 0]) &
            (bb[:, None, 1] < bq[None, :, 3]) & (bb[:, None, 3] > bq[None, :, 1]))
    ii, jj = np.nonzero(cand)
    if ii.size == 0:
        return out

    inter = shapely.area(shapely.intersection(pb[ii], pq[jj]))

    a1 = (boxes[:, 2] * boxes[:, 3])[ii]
    a2 = (query_boxes[:, 2] * query_boxes[:, 3])[jj]
    if criterion == -1:
        den = a1 + a2 - inter
        val = np.where(den > 0, inter / np.where(den > 0, den, 1.0), 0.0)
    elif criterion == 0:
        val = np.where(a1 > 0, inter / np.where(a1 > 0, a1, 1.0), 0.0)
    elif criterion == 1:
        val = np.where(a2 > 0, inter / np.where(a2 > 0, a2, 1.0), 0.0)
    else:
        val = inter          # raw intersection area

    out[ii, jj] = val.astype(np.float32)
    return out
