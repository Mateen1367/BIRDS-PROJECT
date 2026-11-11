# Presentation plan: Which Texas Bird Is It?

DATA 4380 · Computer vision project · Presenting **Wednesday, November 18, 2026**
Same rubric and 20-slide structure as the tabular project (Dr. Rostami confirmed).

## Speaker split (7–10 min each, 21+ min total)

| Speaker | Slides | Part |
|---|---|---|
| Mateen | 1–7 | Problem, previous work, data, EDA, minimum preprocessing |
| Tej | 8–13 | Baseline, augmentation, transfer learning, model selection, improvement, tuning |
| Alejandro | 14–20 | Comparison, interpretation, findings, limitations, conclusion, references, questions |

## Slide plan

| # | Slide | Main content | Source |
|---|---|---|---|
| 1 | Title | Which Texas Bird Is It? Classifying 10 Species with CNNs | |
| 2 | Background & motivation | Bird-ID apps, citizen science, wildlife monitoring; why Texas | |
| 3 | Previous work | Merlin Photo ID · CUB-200-2011 · BIRDS 525 transfer learning · shortcut learning | below |
| 4 | Question & objectives | 10-class image classification; 4 objectives; success = beat baseline clearly + explain errors | README |
| 5 | Dataset | BIRDS 525 subset, CC0, 1,710 images, 224×224, balance chart | nb1 §1–4 |
| 6 | EDA | Lookalike pairs, outliers, **sky-background chart** (hawks ~33% sky) | nb1 §5–7 |
| 7 | Minimum preprocessing | Checks, stratified split, 128 px, 0–1 scaling | nb1 §8–9 |
| 8 | Baseline | Majority guess → simple CNN, macro F1 | nb2 §3–4 |
| 9 | Additional preprocessing | Augmentation; effect on validation F1 | nb2 §5 |
| 10 | Feature engineering (images) | Transfer-learned ImageNet features replace hand-made features | nb2 §6 |
| 11 | Model selection | CNN vs. MobileNetV2: why, strengths, limits, preprocessing needs | nb2 §4, §6 |
| 12 | Model improvement | Improvement ladder chart, each step credited | nb2 §8 |
| 13 | Hyperparameter tuning | 2×2 grid, validation only, before/after | nb2 §7 |
| 14 | Model comparison | Test table: accuracy, precision, recall, F1, ROC-AUC | nb2 §9 |
| 15 | Interpretation | Confusion matrix, lookalike errors, Grad-CAM | nb2 §9–11 |
| 16 | Key findings | Answer each objective | |
| 17 | Limitations | Small data, web photos, cropped/centered images, background shortcut, 10 species only | |
| 18 | Conclusion & future work | More species, real camera-trap photos, location/date like Merlin | |
| 19 | References | APA | below |
| 20 | Questions | | |

## Previous work (slide 3)

1. **Merlin Photo ID (Cornell Lab of Ornithology & Visipedia).** A deep CNN trained on millions of birder-submitted eBird / Macaulay Library photos; recognizes 400+ common North American species. The user also gives location, date and clicks on the bill, eye and tail. Reported to have the right bird in its **top 3 about 90%** of the time. *Ours vs. theirs:* same task, far smaller scale; we use the photo only, no location/date.
2. **CUB-200-2011 (Wah et al., 2011).** The standard *fine-grained* bird benchmark: 200 species, 11,788 images with part annotations. The original baselines reached only ~10–17% accuracy, showing how hard telling similar birds apart is; modern deep models reach roughly 85–95%. *Ours vs. theirs:* the same "lookalike species" challenge at a smaller scale (10 species).
3. **Transfer learning on BIRDS 525 (e.g., EfficientNet-B2 project).** Kaggle-style projects fine-tune ImageNet models on all 525 species and report ~99% accuracy, because images are clean, cropped and centered. *Ours vs. theirs:* we use a smaller, faster model (MobileNetV2), and we ask **what the model looks at**, not just its score.
4. **Shortcut learning (Geirhos et al., 2020; Ribeiro et al., 2016).** Networks often succeed for the wrong reason, like the well-known "wolf vs. husky" classifier that used snow in the background. *Why it matters to us:* hawks in our data appear against sky far more than other birds, so we check with Grad-CAM.

## References (APA)

- Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence, 2*(11), 665–673. https://doi.org/10.1038/s42256-020-00257-z
- Piosenka, G. (2023). *BIRDS 525 species – Image classification* [Data set]. Kaggle. Mirror: https://huggingface.co/datasets/chriamue/bird-species-dataset (CC0 1.0)
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135–1144.
- Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). MobileNetV2: Inverted residuals and linear bottlenecks. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, 4510–4520.
- Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. *Proceedings of the IEEE International Conference on Computer Vision*, 618–626.
- Wah, C., Branson, S., Welinder, P., Perona, P., & Belongie, S. (2011). *The Caltech-UCSD Birds-200-2011 dataset* (Technical Report CNS-TR-2011-001). California Institute of Technology.
- Cornell Lab of Ornithology. (n.d.). *Merlin Bird ID* [Mobile app]. https://merlin.allaboutbirds.org
- Abadi, M., et al. (2015). *TensorFlow: Large-scale machine learning on heterogeneous systems*. https://www.tensorflow.org
