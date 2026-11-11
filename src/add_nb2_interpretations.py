"""Insert the written interpretation cells into notebook 2 after it has been executed.

The numbers quoted here come from the executed run saved in reports/results.json.
Run from the repo root after executing the notebook:  python src/add_nb2_interpretations.py
"""
import json
from pathlib import Path

import nbformat as nbf

NB = Path("notebooks/02_modeling_and_evaluation.ipynb")
nb = nbf.read(NB, as_version=4)

notes = {
    # anchor text in a code cell -> markdown to insert right after it
    'fit("1. Baseline CNN"': """**What this shows:** the baseline CNN reaches **validation macro F1 0.608** (60.9% accuracy). That's far above the majority guess (0.022), so the CNN is learning real visual patterns. But it still gets about 4 in 10 birds wrong. It was also still improving when it hit the 30-epoch limit (train accuracy 68%, validation 63%), so it is somewhat **under-trained** rather than overfit.""",
    'fit("2. CNN + augmentation"': """**What happened:** augmentation **lowered** validation macro F1 from **0.608 to 0.558**. The rubric asks us to report steps that didn't help, so here it is. Our explanation: with only ~120 photos per bird and ~30 epochs, a small CNN learning from scratch has a hard enough time learning the birds; adding random changes makes the task harder still, and it needs much longer training to benefit. Its final epoch shows train accuracy 61% vs. validation 48%, so it hadn't settled.""",
    'fit("3. MobileNetV2 frozen"': """**What this shows:** transfer learning is the big jump: validation macro F1 goes from **0.608 (baseline) to 0.956**, while training only **12,810 weights** (just the new output layer) instead of 242,122. The pretrained features already "know" feathers, beaks and eyes from ImageNet.""",
    'fit("3b. MobileNetV2 frozen, no augmentation"': """**What this shows:** without augmentation, MobileNetV2 scores slightly *higher* (validation F1 **0.964 vs. 0.956**, about 2 more images right out of 256). So augmentation didn't help either model here. A likely reason: the images are already clean, centered and similarly framed, so random flips, rotations and zooms mostly add noise. Because the gap is only about 2 images, we read it as "no benefit" rather than "harmful".""",
    "tuning = pd.DataFrame(tuning)": """**What this shows:** fine-tuning did **not** beat the frozen model. The best combination (top 30 layers, learning rate 1e-5, validation F1 **0.960**) is the same as the default, so **tuning changed nothing**. The larger learning rate (3e-5) hurt (0.931–0.939). Early stopping ended most runs after 4 epochs, which means validation loss started rising after the first epoch: the frozen features were already good, and with ~1,200 training images the extra flexibility (1.5 million trainable weights) mostly overfits.""",
    'final_model.save(MODELS / "final_bird_model.keras")': """**Final model: MobileNetV2, frozen, without augmentation.** It has the highest validation macro F1 (**0.964**) *and* the fewest trained weights, so the tie rule wasn't even needed. It's also the simplest transfer-learning model we tried.""",
    'test_table = pd.DataFrame({s: scores(y["test"], test_probs[s]) for s in steps}).T.round(3)': """**What this shows:** on the 257 held-out test images, the final model gets **96.1% accuracy and macro F1 0.964**, vs. **0.679** for the baseline CNN and **0.022** for guessing. Test scores line up closely with validation scores for every model (e.g., final model 0.964 on both), which suggests our validation-based choices were not overfit to the validation set.

*One honest note:* the fine-tuned model also scores 0.955 on test, close to the final model. We did not, and should not, re-pick a model based on test results.""",
    'sns.heatmap(cm, annot=True': """**What this shows:** almost everything sits on the diagonal. The only off-diagonal cells are inside the lookalike pairs: **Red-shouldered ↔ Red-tailed Hawk (5)**, **Crow ↔ Common Grackle (4)** and **Mourning ↔ Rock Dove (1)**. The baseline CNN (orange matrix) made 81 mistakes spread across many species.""",
    "per_class = pd.DataFrame(": """**What this shows:** every species improves over the baseline. Four species are perfect on test (Northern Cardinal, Green Jay, Roadrunner, Northern Mockingbird); the lowest are the two hawks and the black birds (F1 0.91–0.93), exactly the pairs we expected to be hard.""",
    "errors = pd.DataFrame(": """**What this shows:** this answers objective 4. **All 10 of the final model's mistakes are inside a lookalike pair, and none are "random"**. The baseline CNN made 81 mistakes, and 49 of them were outside the pairs (e.g., confusing very different birds).""",
    'plt.suptitle("Final model\'s mistakes on the test set"': """**What this shows:** the mistakes are understandable. Hawks photographed from behind or in flight hide the chest and tail colors that separate the two species, and grackles in poor light lose their purple sheen and look like crows. **7 of the 10 mistakes had confidence under 65%**, so the model is usually unsure when it's wrong; a real app could say "not sure" below a threshold. The mislabeled-looking "Mourning Dove" (it has a black neck ring like a collared dove) also hints at some **label noise** in the web-collected data.""",
    'plt.suptitle("Grad-CAM: where the final model looks': """**What this shows:** for most birds the heat sits **on the bird's body**: the hawk's chest and tail, the crow's body, the grackle's head and neck. This is the plumage that actually separates these species. One exception: for the "Rock Dove" example the model focused on the top-left corner. That photo also looks like a *speckled pigeon* rather than a rock dove, another possible label-noise case.""",
    "print(f\"Outer frame = {frame.mean():.0%} of the image area\")": """**What this shows:** the outer frame covers 49% of the image, but it receives only **17–34%** of the heatmap's weight for every species. Even for hawks, the "sky" species from notebook 1, it's 23–27%. So the final model mostly looks at the **center, where the bird is**, rather than relying on the sky background. This reduces, though doesn't fully rule out, the shortcut-learning concern.""",
}

summary = """## 14. Summary: answering our objectives

| Objective | Answer |
|---|---|
| 1. Baseline | Simple CNN with minimum preprocessing: **validation macro F1 0.608**, test 0.679. Majority guess: 0.022. |
| 2. Step-by-step improvement | **Transfer learning** gave the whole gain (0.608 → 0.956 validation). Augmentation **did not help** (CNN 0.608 → 0.558; MobileNetV2 0.956 vs. 0.964 without). Fine-tuning and tuning **did not help** (best 0.960 = the default setting). |
| 3. Final evaluation (test, used once) | **MobileNetV2, frozen, no augmentation: 96.1% accuracy, macro F1 0.964, ROC-AUC 0.999**, on 257 images it never trained on. |
| 4. Lookalikes and backgrounds | **All 10 test mistakes are inside the lookalike pairs** (5 hawks, 4 crow/grackle, 1 dove). Grad-CAM shows the model mostly looks at the bird, not the sky. |

**Main takeaway:** with only ~120 photos per species, *reusing* a network trained on millions of photos matters far more than anything we tuned ourselves. The remaining errors are the hard, genuinely similar species: the same pairs a beginner birder would mix up.

**What we would not claim:** these photos are clean, cropped and centered, and many come from the web. 96% here does **not** mean 96% on blurry backyard or camera-trap photos, or on species outside our 10. The model will always answer with one of the 10 birds, even for a photo of a penguin."""

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
