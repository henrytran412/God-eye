"""Export the FlashOcc/BEVDet image backbone to ONNX for Jetson benchmarking.

Why this script exists. Getting the *whole* FlashOcc stack running on a Jetson
means mmdet3d, a custom `bev_pool_v2` CUDA op, and an 8 GB memory budget -- days
of dependency work before a single number appears. But FlashOcc is

    image backbone (R50)  ->  LSS view transform  ->  BEV encoder  ->  occ head

and the image backbone runs on all six nuScenes cameras every frame, so its
latency is a hard lower bound on the whole model's latency. Benchmarking just
the backbone is therefore a legitimate first result: it proves the TensorRT
toolchain works on the device and it bounds what the full model can ever
achieve. If the backbone alone cannot hit the frame budget, the full model
certainly cannot, and that is worth knowing in week one rather than month four.

This script runs on a normal laptop -- CPU-only PyTorch is fine, no GPU needed.
Copy the resulting .onnx to the Jetson and benchmark it with bench_trt.py.

Input shape follows the BEVDet/FlashOcc nuScenes convention: six surround-view
cameras at 256x704 per image, processed as one batch of six.
"""
import argparse
import pathlib
import sys

import torch
import torch.nn as nn
import torchvision


# nuScenes surround-view rig: 6 cameras. BEVDet/FlashOcc R50 crops to 256x704.
N_CAMS = 6
IMG_H = 256
IMG_W = 704


class BackboneNeck(nn.Module):
    """ResNet-50 trunk plus an FPN-style 1x1 lateral, as BEVDet uses it.

    The real BEVDet neck fuses C3/C4/C5; this keeps C3 and C5 and projects to a
    fixed width. It is deliberately a stand-in, not a reimplementation -- the
    point is to measure the cost of the convolutional trunk that dominates
    backbone latency, not to reproduce FlashOcc's accuracy.
    """

    def __init__(self, out_channels: int = 256):
        super().__init__()
        r50 = torchvision.models.resnet50(weights=None)
        self.stem = nn.Sequential(r50.conv1, r50.bn1, r50.relu, r50.maxpool)
        self.layer1 = r50.layer1
        self.layer2 = r50.layer2   # C3, stride 8,  512ch
        self.layer3 = r50.layer3   # C4, stride 16, 1024ch
        self.layer4 = r50.layer4   # C5, stride 32, 2048ch
        self.lateral_c5 = nn.Conv2d(2048, out_channels, 1)
        self.lateral_c3 = nn.Conv2d(512, out_channels, 1)
        self.fuse = nn.Conv2d(out_channels, out_channels, 3, padding=1)

    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        c3 = self.layer2(x)
        c4 = self.layer3(c3)
        c5 = self.layer4(c4)
        up = nn.functional.interpolate(
            self.lateral_c5(c5), size=c3.shape[-2:], mode="nearest")
        return self.fuse(self.lateral_c3(c3) + up)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="onnx/backbone_r50_6x256x704.onnx")
    ap.add_argument("--cams", type=int, default=N_CAMS)
    ap.add_argument("--height", type=int, default=IMG_H)
    ap.add_argument("--width", type=int, default=IMG_W)
    ap.add_argument("--opset", type=int, default=17)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    model = BackboneNeck().eval()
    dummy = torch.randn(args.cams, 3, args.height, args.width)

    with torch.no_grad():
        y = model(dummy)
    n_par = sum(p.numel() for p in model.parameters())
    print(f"input   {tuple(dummy.shape)}")
    print(f"output  {tuple(y.shape)}")
    print(f"params  {n_par/1e6:.1f} M")

    torch.onnx.export(
        model, (dummy,), str(out),
        input_names=["imgs"], output_names=["feats"],
        opset_version=args.opset,
        dynamo=False,          # TorchScript path: no `onnx` python pkg required
        do_constant_folding=True,
    )
    size_mb = out.stat().st_size / 1e6
    print(f"wrote   {out}  ({size_mb:.1f} MB)")

    # Verify the exported graph actually loads and runs, so a broken export is
    # caught here rather than on the Jetson.
    try:
        import onnxruntime as ort
    except ImportError:
        print("onnxruntime not installed - skipping verification")
        return 0
    sess = ort.InferenceSession(str(out), providers=["CPUExecutionProvider"])
    got = sess.run(None, {"imgs": dummy.numpy()})[0]
    err = float((torch.from_numpy(got) - y).abs().max())
    print(f"verify  onnxruntime output matches torch, max abs diff {err:.2e}")
    if err > 1e-3:
        print("WARNING: export mismatch is larger than expected")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
