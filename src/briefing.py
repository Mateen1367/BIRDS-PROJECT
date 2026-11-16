"""'Read this first' summary of everything we did in the code, for the front of the speaker scripts.
Items may use <b>bold</b>. Numbers match reports/results.json and the notebooks."""

INTRO = ("Read this before the speaker notes. It's everything we did in the code, in order, so any of us can answer "
         "the professor's questions about the data, the models and the results.")

SECTIONS = [
    ("1. What kind of problem is this?", [
        "<b>Supervised, multi-class image classification.</b> Supervised = every photo has a correct label. Multi-class = "
        "10 possible answers, and each photo gets exactly one (single-label).",
        "<b>Input:</b> one color photo (224 × 224 pixels × 3 colors). <b>Output:</b> 10 probabilities that add up to 100% "
        "(softmax); the highest one is the prediction.",
        "<b>Target:</b> the bird species. <b>Main metric:</b> macro F1 (the F1 score averaged over the 10 species, each counted "
        "equally). We also report accuracy, macro precision, macro recall and ROC-AUC (one-vs-rest).",
        "<b>Tools:</b> Python, TensorFlow/Keras for the models, scikit-learn for the metrics, pandas and matplotlib. Everything ran "
        "on a laptop CPU (no GPU). We limited TensorFlow to 4 threads so the laptop didn't overheat; notebook 2 takes about 25 minutes.",
    ]),
    ("2. The data (notebook 1)", [
        "<b>Source:</b> BIRDS 525 Species by Gerald Piosenka (525 species, ~90,000 photos). The Kaggle page was taken down, so we "
        "downloaded the identical files from a Hugging Face mirror. License: CC0 (public domain).",
        "<b>We kept 10 Texas species = 1,710 photos:</b> Northern Cardinal, Northern Mockingbird, Roadrunner, Green Jay, plus three "
        "lookalike pairs: Mourning Dove vs. Rock Dove, Red-tailed vs. Red-shouldered Hawk, Crow vs. Common Grackle.",
        "<b>Quality checks:</b> 0 broken files, 0 exact duplicates (checked with an MD5 hash of each file), all photos 224 × 224 RGB, "
        "no missing labels. Classes are fairly balanced: 142 to 212 photos per species (ratio 1.49), so no resampling was needed.",
        "<b>Outliers:</b> we computed each photo's brightness and contrast and flagged anything more than 3 standard deviations from "
        "the average: 22 photos (1.3%). We looked at them: real photos (night sky, snow, bright sky), so we <b>kept</b> them.",
        "<b>Sky check:</b> we measured how much of each photo's outer border is blue sky. Hawks ≈ 33%, Green Jay/Roadrunner 3–5%. "
        "Risk: the model could learn \"sky = hawk\" (shortcut learning). That's why we used Grad-CAM at the end.",
        "<b>Our own split:</b> the original test set had only 5 photos per species, too few. We pooled all 1,710 and made a "
        "<b>stratified 70/15/15 split</b> (random seed 42): <b>1,197 train / 256 validation / 257 test</b>, about 25 test photos per bird. "
        "Train = teaches the model, validation = chooses between models, test = used once at the end.",
    ]),
    ("3. How every model was trained", [
        "Photos are loaded with tf.data, decoded, resized, and fed in <b>batches of 32</b>; training photos are reshuffled every epoch.",
        "<b>Optimizer:</b> Adam. <b>Loss:</b> sparse categorical cross-entropy (labels are integers 0–9). <b>Output layer:</b> Dense(10) "
        "with softmax.",
        "<b>Early stopping:</b> watches validation loss; if it doesn't improve for a few epochs (\"patience\"), training stops and the "
        "best epoch's weights are restored. One epoch = one pass through all 1,197 training photos.",
        "Same random seed (42) for every model, so differences come from the model, not luck.",
    ]),
    ("4. The models, step by step (notebook 2)", [
        "<b>Step 0, majority guess:</b> always predict the most common training species (Red-tailed Hawk, 148 photos). The floor: "
        "12.5% accuracy, macro F1 0.02.",
        "<b>Step 1, baseline CNN (from scratch):</b> input 128 × 128 (resized for speed), pixels scaled 0–255 → 0–1. Four blocks of "
        "Conv2D (32, 64, 128, 128 filters, 3 × 3, ReLU) each followed by 2 × 2 max-pooling, then global average pooling, 30% dropout and "
        "Dense(10, softmax). <b>242,122 trainable weights.</b> Adam learning rate 0.001, up to 30 epochs, patience 5. It ran all 30 "
        "epochs (still improving: train 68% vs. validation 63%). <b>Validation macro F1 0.608.</b>",
        "<b>Step 2, same CNN + data augmentation:</b> random horizontal flip, rotation ±10% of a full turn (±36°), zoom ±10%, contrast ±20%, "
        "on training photos only. Up to 40 epochs, patience 6 (ran 28). <b>Validation F1 dropped to 0.558</b>, so it didn't help.",
        "<b>Step 3, MobileNetV2 transfer learning (frozen) + augmentation:</b> MobileNetV2 pretrained on ImageNet (~1.3 million photos, "
        "1,000 categories). We removed its 1,000-class top (include_top=False), froze all its layers, and added global average pooling → "
        "30% dropout → Dense(10, softmax). Input 224 × 224, pixels scaled to −1…1 (MobileNetV2's preprocess_input). "
        "<b>Only 12,810 trainable weights</b> (1,280 features × 10 + 10). Adam 0.001, up to 15 epochs, patience 4. <b>Validation F1 0.956.</b>",
        "<b>Step 3b, same as step 3 without augmentation:</b> <b>validation F1 0.964</b>, the highest. <b>This is our final model.</b>",
        "<b>Steps 4–5, fine-tuning + tuning:</b> starting from the step-3 weights, we unfroze MobileNetV2's top layers (about 1.5 million "
        "trainable weights) and retrained with a tiny learning rate. Grid search of 2 × 2 = 4 runs, scored on validation only: "
        "top 30 or 60 layers × learning rate 1e-5 or 3e-5, up to 8 epochs, patience 3. Results: 30/1e-5 = 0.960 (best, and it was the "
        "default), 60/1e-5 = 0.955, 60/3e-5 = 0.939, 30/3e-5 = 0.931. Most runs stopped after 4 epochs, so <b>fine-tuning didn't beat "
        "the frozen model</b>.",
    ]),
    ("5. How we picked the final model", [
        "Rule set before looking at test scores: <b>highest validation macro F1; if models are within 0.005 (less than one photo), keep "
        "the simpler one</b> (fewest trainable weights). Frozen MobileNetV2 without augmentation was both the best (0.964) and the simplest.",
        "Then all models were scored <b>once</b> on the 257 test photos. The test set never chose anything.",
    ]),
    ("6. Interpreting the final model", [
        "<b>Confusion matrix:</b> 10 mistakes out of 257, <b>all inside the lookalike pairs</b>: 5 hawk ↔ hawk, 4 crow ↔ grackle, "
        "1 mourning dove → rock dove. The baseline CNN made 81 mistakes (49 outside the pairs).",
        "<b>Per species (test F1):</b> Cardinal, Green Jay, Roadrunner and Mockingbird 1.00; Mourning Dove 0.98; Rock Dove 0.98; "
        "Common Grackle 0.93; Crow 0.92; Red-tailed Hawk 0.92; Red-shouldered Hawk 0.91.",
        "<b>Confidence:</b> 7 of the 10 mistakes had confidence under 65%, so the model is usually unsure when it's wrong.",
        "<b>Grad-CAM:</b> a heatmap from the gradients of the predicted species' score with respect to MobileNetV2's last convolution "
        "output (7 × 7 × 1,280). The outer 32-pixel frame is 49% of the image area but gets only 17–34% of the heatmap for every species "
        "(hawks 23–27%), so the model mostly looks at the bird, not the sky. One rock dove photo was an exception (heat in a corner) and "
        "looks like a different pigeon species, suggesting a label error.",
    ]),
]

RESULTS = [["Step", "Model", "Trainable weights", "Val. F1", "Test F1", "Test accuracy"],
           ["0", "Majority guess", "0", "0.022", "0.022", "12.5%"],
           ["1", "Baseline CNN (from scratch)", "242,122", "0.608", "0.679", "68.5%"],
           ["2", "CNN + augmentation", "242,122", "0.558", "0.559", "55.6%"],
           ["3", "MobileNetV2 frozen + augmentation", "12,810", "0.956", "0.936", "93.4%"],
           ["3b", "MobileNetV2 frozen, no aug. (FINAL)", "12,810", "0.964", "0.964", "96.1%"],
           ["4–5", "Fine-tuned (best of grid = default)", "~1.5 million", "0.960", "0.955", "95.3%"]]

QA = [
    ("What type of classification is this?", "Supervised, single-label, multi-class image classification with 10 classes."),
    ("What model did you end up with?", "MobileNetV2 pretrained on ImageNet, all layers frozen, with a new 10-class softmax layer on top. "
     "Only 12,810 weights were trained. No augmentation."),
    ("What's your accuracy?", "96.1% on 257 test photos (macro F1 0.964), vs. 68.5% for our from-scratch CNN baseline and 12.5% for guessing."),
    ("Why macro F1?", "It averages F1 over all 10 species equally, so the model can't look good by ignoring one bird. Our classes are "
     "fairly balanced, so accuracy is also meaningful."),
    ("Why didn't augmentation help?", "The from-scratch CNN only had ~120 photos per bird and 30–40 epochs; random changes made learning "
     "harder. For MobileNetV2 the photos are already clean and centered, so augmentation mostly added noise (0.964 without vs. 0.956 with)."),
    ("Why didn't fine-tuning help?", "Unfreezing ~1.5 million weights with only ~1,200 training photos lets the model memorize. Validation "
     "loss got worse after the first epoch, so early stopping ended most runs at 4 epochs."),
    ("Did you overfit?", "No. The frozen MobileNetV2's training and validation accuracy stay together at about 95% (backup slide 23). The from-scratch CNN was under-"
     "trained rather than overfit (68% train vs. 63% validation at 30 epochs)."),
    ("How did you avoid data leakage?", "One stratified split made before any training, no photo (by file hash) in two splits, augmentation "
     "only on training photos, and every choice made on validation. Test used once."),
    ("Why MobileNetV2 and not ResNet or EfficientNet?", "It's small and fast enough to train in minutes on a laptop CPU, and it already "
     "reached 96%. A bigger model might add a point at much higher cost."),
    ("What's Grad-CAM?", "A heatmap showing which parts of the photo pushed the model toward its answer, built from the gradients of the "
     "predicted class with respect to the last convolution layer."),
    ("Would 96% hold on real photos?", "Probably not fully. These photos are clean, cropped and centered; real backyard photos are blurrier "
     "and farther away. And the model only knows these 10 species."),
]
