# KAAVAL Fine-Tuning Playbook

- **Objective**: align face recognition embeddings with local demographic bias using ArcFace backbone.
- **Dataset**: curated missing-person pairs, augmented with GAN-generated occlusions and lighting shifts. Stored under `datasets/kaaval_pairs/`.
- **Schedule**: 12 epochs, cosine LR from 5e-4 to 1e-6, batch size 64 on RTX 4090.
- **Augmentations**: random erasing (p=0.3), color jitter (±12%), gaussian blur (σ≤1.2), synthetic scar overlays (p=0.15).
- **Validation**: hold-out 10% by identity, evaluate ROC AUC, TPR@FPR=1%, top-5 recall.
- **Specialist Models**: fine-tune demographic-specific heads with class-balanced sampling per cohort.
- **Logging**: WandB project `kaaval-finetune`, log gradients + confusion matrices per cohort.
- **Deployment**: export to ONNX, register in `models/manifest.json`, trigger FAISS index rebuild.

