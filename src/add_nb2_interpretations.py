"""Insert the written interpretation cells into notebook 2 after it has been executed.

The numbers quoted here come from the executed run saved in reports/results.json.
Run from the repo root after executing the notebook:  python src/add_nb2_interpretations.py
"""
from pathlib import Path

import nbformat as nbf

NB = Path("notebooks/02_modeling_and_evaluation.ipynb")
nb = nbf.read(NB, as_version=4)

notes = {
    # anchor text in a code cell -> markdown to insert right after it
    'fit("1. Baseline CNN"': """**What this shows:** the baseline CNN reaches **validation macro F1 0.608** (60.9% accuracy, loss 0.983). That's far above the majority guess (0.022), so the CNN is learning real visual patterns, but it still gets about 4 in 10 birds wrong. It was still improving when it hit the 30-epoch limit (train accuracy 68%, validation 63%), so it is somewhat **under-trained** rather than overfit.""",
    'fit("2. CNN + augmentation"': """**What happened:** augmentation **lowered** validation macro F1 from **0.608 to 0.558**. With only ~120 photos per bird and ~30 epochs, a small CNN learning from scratch already struggles; random changes make the task harder still, and it would need much longer training to benefit.""",
    'fit("3. MobileNetV2 frozen"': """**What this shows:** transfer learning is the big jump: validation macro F1 goes from **0.608 (baseline) to 0.956**, while training only **12,810 weights** (just the new output layer) instead of 242,122.""",
    'fit("3b. MobileNetV2 frozen, no augmentation"': """**What this shows:** without augmentation, MobileNetV2 scores slightly *higher* (validation F1 **0.964 vs. 0.956**, about 2 more photos right out of 256). Augmentation didn't help either model here, probably because the photos are already clean and centered. We use **no augmentation** for the second transfer learning model too.""",
    'fit("3c. ResNet50 frozen, no augmentation"': """**What this shows:** ResNet50, used the same way (feature extraction), reaches **validation F1 0.965** with the **lowest validation loss (0.112)**: essentially tied with MobileNetV2 (0.964). It's about 4× slower to train on our laptop (12.6 vs. 3.2 minutes) because it's a much bigger network.""",
    "tuning = pd.DataFrame(tuning)": """**What this shows:** fine-tuning did **not** beat the frozen models. The best combination (top 60 layers, learning rate 1e-5) reached validation F1 **0.959**, only slightly above the default (0.955) and still below frozen MobileNetV2 (0.964). The larger learning rate (3e-5) hurt (0.920–0.927). Early stopping ended every run after 4 epochs, which means validation loss started rising after the first epoch: with ~1,200 training photos, unfreezing 1.5 million weights mostly overfits.""",
    'final_model.save(MODELS / "final_bird_model.keras")': """**Result of the rule:** MobileNetV2 (0.964) and ResNet50 (0.965) are within 0.005 on validation, less than one photo, so they count as **tied**, and the rule keeps the simpler **MobileNetV2** (12,810 vs. 20,490 trained weights, 2.3 vs. 23.6 million frozen weights, about 4× faster). This saved model is used for the heatmaps and the upload demo below.""",
    'results_test_loss = test_table["loss"].to_dict()': """**What this shows:** on the 257 held-out test photos, both transfer learning models are far ahead of the baseline (macro F1 0.679, accuracy 68.5%, loss 0.857):

- **ResNet50: 98.1% accuracy, macro F1 0.982, loss 0.095: the strongest model on the test set** (5 mistakes)
- **MobileNetV2: 96.1% accuracy, macro F1 0.964, loss 0.118** (10 mistakes)

The two were tied on validation, so ResNet50's lead only appears on test. We report it honestly, but we don't re-pick the saved model based on test results. **Why ResNet50 did better:** it's a much deeper network (50 layers) that produces richer features (2,048 numbers per photo vs. 1,280), which helps with fine details like a hawk's chest pattern or a grackle's eye. The trade-off is size and speed.""",
    'class_reports[SHORT[name]] = classification_report': """**What this shows:** the baseline struggles most with the lookalikes (Red-tailed Hawk recall 0.38, Rock Dove 0.43). Both transfer learning models are perfect or near perfect on the distinctive birds, and their lowest scores are on the hawks and the crow/grackle pair, exactly the pairs we expected to be hard. ResNet50's lowest species F1 is 0.96; MobileNetV2's is 0.91.""",
    'plt.savefig(FIG / "confusion_matrices_all.png"': """**What this shows:** the baseline's 81 mistakes are spread across many species (e.g., 15 Red-tailed Hawks called Red-shouldered, 8 mockingbirds called mourning doves). MobileNetV2's 10 mistakes are **all** inside the lookalike pairs (5 hawk, 4 crow/grackle, 1 dove). ResNet50 makes 5: 2 hawk, 2 crow/grackle, and 1 roadrunner called a mockingbird.""",
    "per_class = pd.DataFrame(": """**What this shows (saved model, MobileNetV2):** every species improves over the baseline. Four species are perfect on test (Northern Cardinal, Green Jay, Roadrunner, Northern Mockingbird); the lowest are the two hawks and the black birds (F1 0.91–0.93).""",
    "errors = pd.DataFrame(": """**What this shows:** all 10 of MobileNetV2's mistakes are inside a lookalike pair, and none are "random". The baseline CNN made 81 mistakes, 49 of them outside the pairs.""",
    'plt.suptitle("Final model\'s mistakes on the test set"': """**What this shows:** the mistakes are understandable. Hawks photographed from behind or in flight hide the chest and tail colors that separate the two species, and grackles in poor light lose their purple sheen and look like crows. **7 of the 10 mistakes had confidence under 65%**, so the model is usually unsure when it's wrong. The "Mourning Dove" with a black neck ring looks like a collared dove, which hints at some **label noise** in the web-collected data.""",
    'plt.suptitle("Grad-CAM: where the final model looks': """**What this shows:** for most birds the heat sits **on the bird's body** (the hawk's chest and tail, the crow's body, the grackle's head), the plumage that actually separates these species. One exception: for the "Rock Dove" example the model focused on the top-left corner; that photo also looks like a *speckled pigeon*, another possible label-noise case.""",
    'print(f"Outer frame = {frame.mean():.0%} of the image area")': """**What this shows:** the outer frame covers 49% of the image but receives only **17–34%** of the heatmap's weight for every species, including the "sky" hawks (23–27%). So the model mostly looks at the **center, where the bird is**, rather than relying on the sky background.""",
}

summary = """## 14. Summary

| | Baseline CNN | MobileNetV2 (transfer) | ResNet50 (transfer) |
|---|---|---|---|
| How it was used | Trained from scratch | Feature extraction (frozen) | Feature extraction (frozen) |
| Trained weights | 242,122 | 12,810 | 20,490 |
| Validation macro F1 | 0.608 | 0.964 | 0.965 |
| **Test accuracy** | 68.5% | 96.1% | **98.1%** |
| Test loss | 0.857 | 0.118 | **0.095** |
| Test mistakes (of 257) | 81 | 10 | **5** |

- **Transfer learning made the difference:** both pretrained models beat our from-scratch CNN by about 28–30 accuracy points.
- **Strongest model: ResNet50** on the test set (98.1%). On validation the two pretrained models were tied, and by our rule we saved the smaller, faster MobileNetV2.
- **Steps that didn't help:** augmentation (both models tested) and fine-tuning MobileNetV2 (best 0.959 vs. 0.964 frozen).
- **Mistakes are lookalikes:** MobileNetV2's 10 errors are all inside the hawk, crow/grackle and dove pairs, and Grad-CAM shows it looks at the bird, not the sky.

**What we would not claim:** these photos are clean, cropped and centered, and many come from the web. 96–98% here does **not** mean the same on blurry backyard photos or on species outside our 10."""

inserted = 0
cells = []
for c in nb.cells:
    cells.append(c)
    if c.cell_type == "code":
        for anchor, text in notes.items():
            if anchor in c.source:
                cells.append(nbf.v4.new_markdown_cell(text))
                inserted += 1
nb.cells = [c for c in cells if not (c.cell_type == "markdown" and "SUMMARY_TEXT" in c.source)]
nb.cells.append(nbf.v4.new_markdown_cell(summary))
nbf.write(nb, NB)
print(f"inserted {inserted} of {len(notes)} notes + summary")
