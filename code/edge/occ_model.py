"""FlashOcc-shaped occupancy network in plain PyTorch, built for ONNX export.

Purpose. Benchmarking a bare ResNet-50 tells your advisor nothing about
occupancy -- he will say "that is a classifier, not FlashOcc." This module
reproduces FlashOcc's *architecture and tensor shapes* without mmdet3d, mmcv,
or the custom `bev_pool_v2` CUDA op, so it exports to ONNX and runs under
TensorRT on a Jetson today rather than after two weeks of dependency work.

    6 cameras -> R50 backbone -> DepthNet (D depth bins + C context)
              -> LSS view transform -> BEV 200x200 -> BEV encoder
              -> channel2height head -> 200x200x16x18

What this IS: a faithful reproduction of the computational shape, so the
latency, memory and power numbers are representative of the real model.

What this IS NOT: trained. There are no pretrained weights here and it predicts
nothing meaningful. Every number from it is a COST measurement, never an
accuracy measurement. Say that plainly whenever you show the numbers, or the
result is worthless the moment someone checks.

The one genuine approximation is the view transform. Real FlashOcc uses a
custom CUDA kernel (`bev_pool_v2`) to scatter frustum features into BEV cells.
That op has no ONNX equivalent, so `--view-transform` offers:

  scatter  index_add_ into the BEV grid. Exports as ScatterND. Honest about the
           memory traffic, but TensorRT may implement it slower than the real
           custom kernel -- so this is an UPPER bound on that stage.
  skip     omit the stage entirely and pool the frustum directly. Gives a LOWER
           bound on total latency.

Reporting both brackets the true value, which is more useful than one number
of unknown bias. Say "between X and Y ms" and you are being accurate.
"""
import argparse
import pathlib
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

# BEVDet / FlashOcc nuScenes configuration
N_CAMS = 6
IMG_H, IMG_W = 256, 704
DOWNSAMPLE = 16          # R50 C4 stride used by BEVDet's LSS
D_BINS = 59              # depth bins, 1..60 m at 1 m
C_CTX = 80               # context channels per frustum point
BEV_H = BEV_W = 200      # +-40 m at 0.4 m
BEV_C = 256
OCC_Z = 16               # height bins
OCC_CLS = 18             # 17 semantic classes + free


class DepthNet(nn.Module):
    """Predicts a depth distribution and a context feature per pixel (LSS)."""

    def __init__(self, in_ch: int, d_bins: int = D_BINS, c_ctx: int = C_CTX):
        super().__init__()
        self.reduce = nn.Sequential(
            nn.Conv2d(in_ch, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(True))
        self.depth = nn.Conv2d(256, d_bins, 1)
        self.context = nn.Conv2d(256, c_ctx, 1)
        self.d_bins, self.c_ctx = d_bins, c_ctx

    def forward(self, x):
        x = self.reduce(x)
        depth = self.depth(x).softmax(dim=1)          # (N, D, h, w)
        ctx = self.context(x)                          # (N, C, h, w)
        # Outer product over the depth axis -> frustum features (N, D, C, h, w).
        # This is the memory hot-spot of every LSS model and the main reason
        # occupancy nets are hard to fit on an 8 GB board; keep it in the graph.
        return depth.unsqueeze(2) * ctx.unsqueeze(1)


class BEVEncoder(nn.Module):
    """Small ResNet-style trunk over the BEV grid."""

    def __init__(self, in_ch: int = C_CTX, width: int = BEV_C):
        super().__init__()
        def block(cin, cout, stride=1):
            return nn.Sequential(
                nn.Conv2d(cin, cout, 3, stride=stride, padding=1, bias=False),
                nn.BatchNorm2d(cout), nn.ReLU(True),
                nn.Conv2d(cout, cout, 3, padding=1, bias=False),
                nn.BatchNorm2d(cout), nn.ReLU(True))
        self.stem = block(in_ch, width // 2)
        self.down1 = block(width // 2, width, stride=2)
        self.down2 = block(width, width, stride=2)
        self.up = nn.Sequential(
            nn.Conv2d(width + width // 2, width, 3, padding=1, bias=False),
            nn.BatchNorm2d(width), nn.ReLU(True))

    def forward(self, x):
        s = self.stem(x)
        d1 = self.down1(s)
        d2 = self.down2(d1)
        u = F.interpolate(d2, size=s.shape[-2:], mode="bilinear",
                          align_corners=False)
        return self.up(torch.cat([u, s], dim=1))


class Channel2HeightHead(nn.Module):
    """FlashOcc's contribution: reshape BEV channels into height, no 3D decoder."""

    def __init__(self, in_ch: int = BEV_C, z: int = OCC_Z, n_cls: int = OCC_CLS):
        super().__init__()
        self.z, self.n_cls = z, n_cls
        self.head = nn.Sequential(
            nn.Conv2d(in_ch, in_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(in_ch), nn.ReLU(True),
            nn.Conv2d(in_ch, z * n_cls, 1))

    def forward(self, x):
        n, _, h, w = x.shape
        return self.head(x).view(n, self.z, self.n_cls, h, w)


class FlashOccShaped(nn.Module):
    def __init__(self, view_transform: str = "scatter", n_cams: int = N_CAMS):
        super().__init__()
        r50 = torchvision.models.resnet50(weights=None)
        self.trunk = nn.Sequential(
            r50.conv1, r50.bn1, r50.relu, r50.maxpool,
            r50.layer1, r50.layer2, r50.layer3)      # C4, stride 16, 1024ch
        self.depthnet = DepthNet(1024)
        self.bev_encoder = BEVEncoder()
        self.occ_head = Channel2HeightHead()
        self.view_transform = view_transform
        self.n_cams = n_cams

        fh, fw = IMG_H // DOWNSAMPLE, IMG_W // DOWNSAMPLE
        n_pts = n_cams * D_BINS * fh * fw
        if view_transform == "scatter":
            # Fixed frustum->BEV assignment. With real calibration these indices
            # come from the camera matrices; for a cost measurement any valid
            # assignment has identical compute, so a deterministic pseudo-random
            # one is used. Registered as a buffer so it exports into the graph.
            g = torch.Generator().manual_seed(0)
            idx = torch.randint(0, BEV_H * BEV_W, (n_pts,), generator=g)
            self.register_buffer("bev_index", idx, persistent=False)

    def forward(self, imgs):                      # (n_cams, 3, H, W)
        feats = self.trunk(imgs)                  # (n_cams, 1024, h, w)
        frustum = self.depthnet(feats)            # (n_cams, D, C, h, w)
        n, d, c, h, w = frustum.shape

        if self.view_transform == "scatter":
            pts = frustum.permute(0, 1, 3, 4, 2).reshape(-1, c)   # (n*D*h*w, C)
            bev = torch.zeros(BEV_H * BEV_W, c, dtype=pts.dtype,
                              device=pts.device)
            # scatter_add, not index_add: many frustum points fall in the same
            # BEV cell, and ONNX cannot export index_add with duplicate indices
            # -- while duplicates are the entire point of BEV pooling. The index
            # must be broadcast to the source shape, which materialises an
            # (n_pts, C) int64 tensor. That memory traffic is exactly why BEVDet
            # ships a custom `bev_pool_v2` kernel, and it is why this path is an
            # upper bound on the real cost rather than an estimate of it.
            idx = self.bev_index.unsqueeze(1).expand(-1, c)
            bev = bev.scatter_add(0, idx, pts)
            bev = bev.permute(1, 0).reshape(1, c, BEV_H, BEV_W)
        else:
            # Lower bound: collapse the frustum and tile to the BEV footprint,
            # skipping the scatter entirely.
            pooled = frustum.mean(dim=(0, 1))                     # (C, h, w)
            bev = F.interpolate(pooled.unsqueeze(0), size=(BEV_H, BEV_W),
                                mode="bilinear", align_corners=False)

        return self.occ_head(self.bev_encoder(bev))   # (1, 16, 18, 200, 200)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--view-transform", choices=["scatter", "skip"],
                    default="scatter")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cams", type=int, default=N_CAMS)
    ap.add_argument("--opset", type=int, default=17)
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args()

    out = pathlib.Path(args.out or
                       f"onnx/flashocc_shaped_{args.view_transform}.onnx")
    out.parent.mkdir(parents=True, exist_ok=True)

    model = FlashOccShaped(args.view_transform, args.cams).eval()
    dummy = torch.randn(args.cams, 3, IMG_H, IMG_W)

    with torch.no_grad():
        y = model(dummy)
    print(f"view transform : {args.view_transform}")
    print(f"input          : {tuple(dummy.shape)}")
    print(f"output         : {tuple(y.shape)}   (batch, Z, classes, H, W)")
    print(f"params         : {sum(p.numel() for p in model.parameters())/1e6:.1f} M")
    fh, fw = IMG_H // DOWNSAMPLE, IMG_W // DOWNSAMPLE
    frustum_elems = args.cams * D_BINS * C_CTX * fh * fw
    print(f"frustum tensor : {args.cams}x{D_BINS}x{C_CTX}x{fh}x{fw} = "
          f"{frustum_elems/1e6:.1f} M elems "
          f"({frustum_elems*4/1e6:.0f} MB fp32 / {frustum_elems*2/1e6:.0f} MB fp16)")

    torch.onnx.export(
        model, (dummy,), str(out),
        input_names=["imgs"], output_names=["occ"],
        opset_version=args.opset, dynamo=False, do_constant_folding=True)
    print(f"wrote          : {out}  ({out.stat().st_size/1e6:.1f} MB)")

    if args.no_verify:
        return 0
    try:
        import onnxruntime as ort
    except ImportError:
        print("onnxruntime not installed - skipping verification")
        return 0
    sess = ort.InferenceSession(str(out), providers=["CPUExecutionProvider"])
    got = sess.run(None, {"imgs": dummy.numpy()})[0]
    err = float((torch.from_numpy(got) - y).abs().max())
    rel = err / max(float(y.abs().max()), 1e-9)
    print(f"verify         : max abs diff {err:.2e} (rel {rel:.2e})")
    return 0 if rel < 1e-3 else 1


if __name__ == "__main__":
    sys.exit(main())
