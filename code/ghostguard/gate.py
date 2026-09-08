"""The lightweight utility gate.

Three heads, matching the proposal: predicted utility, harm probability, and
predictive uncertainty. The uncertainty head is heteroscedastic (it predicts
log-sigma of the utility residual) so it can express two distinct things:

  * epistemic  -- this feature vector is unlike anything in training,
  * label noise -- U(m|S) genuinely varies a lot with the coalition S.

The second one is not usually modelled, and the coalition diagnostic shows it
matters: for roughly a third of messages the spread of U(m|S) across coalitions
exceeds the magnitude of its mean.
"""
import numpy as np
import torch
import torch.nn as nn


class Gate(nn.Module):
    def __init__(self, dim, hidden=64):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
        )
        self.head_u = nn.Linear(hidden, 1)
        self.head_h = nn.Linear(hidden, 1)
        self.head_s = nn.Linear(hidden, 1)

    def forward(self, x):
        z = self.body(x)
        return (self.head_u(z).squeeze(-1),
                self.head_h(z).squeeze(-1),
                self.head_s(z).squeeze(-1).clamp(-4.0, 2.0))


class GateModel:
    """Feature standardisation + training loop + inference."""

    def __init__(self, dim, seed=0, hidden=64):
        torch.manual_seed(seed)
        self.net = Gate(dim, hidden)
        self.mu = np.zeros(dim, dtype=np.float32)
        self.sd = np.ones(dim, dtype=np.float32)

    def fit(self, X, u, harm, epochs=120, bs=512, lr=2e-3, wd=1e-4, verbose=False):
        self.mu = X.mean(axis=0)
        self.sd = X.std(axis=0) + 1e-6
        Xs = torch.tensor((X - self.mu) / self.sd, dtype=torch.float32)
        ut = torch.tensor(u, dtype=torch.float32)
        ht = torch.tensor(harm.astype(np.float32), dtype=torch.float32)
        opt = torch.optim.AdamW(self.net.parameters(), lr=lr, weight_decay=wd)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
        n = len(Xs)
        bce = nn.BCEWithLogitsLoss()
        for ep in range(epochs):
            perm = torch.randperm(n)
            tot = 0.0
            for k in range(0, n, bs):
                idx = perm[k:k + bs]
                pu, ph, ls = self.net(Xs[idx])
                # Gaussian NLL on the utility head gives calibrated sigma
                nll = (0.5 * ((pu - ut[idx]) ** 2) / torch.exp(2 * ls) + ls).mean()
                loss = nll + bce(ph, ht[idx])
                opt.zero_grad()
                loss.backward()
                opt.step()
                tot += float(loss) * len(idx)
            sched.step()
            if verbose and (ep + 1) % 30 == 0:
                print(f"    epoch {ep+1:3d} loss={tot/n:.4f}")
        return self

    @torch.no_grad()
    def predict(self, X):
        if len(X) == 0:
            return np.zeros(0), np.zeros(0), np.zeros(0)
        Xs = torch.tensor((X - self.mu) / self.sd, dtype=torch.float32)
        pu, ph, ls = self.net(Xs)
        return (pu.numpy(), torch.sigmoid(ph).numpy(), torch.exp(ls).numpy())
