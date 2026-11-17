"""'The big picture': a simple overview of the whole project for the front of the speaker scripts.
Items may use <b>bold</b>. Numbers match reports/results.json and the notebooks."""

INTRO = "Read this first. It's the whole project in plain English, so anyone in the group can explain it."

SECTIONS = [
    ("What we did", [
        "We taught computers to <b>look at a bird photo and name the species</b>: 10 Texas birds, so 10 possible answers.",
        "This is called <b>image classification</b> (supervised, multi-class: every photo has one correct label).",
        "We built <b>3 models</b> and compared them: our own small CNN (the <b>baseline</b>), plus two <b>transfer learning</b> models, "
        "<b>MobileNetV2</b> and <b>ResNet50</b>.",
    ]),
    ("The data", [
        "<b>1,710 photos</b> of 10 birds from a public dataset (BIRDS 525, free to use). 142–212 photos per bird, all 224 × 224, bird in the center.",
        "<b>The 10 birds:</b> Northern Cardinal, Northern Mockingbird, Roadrunner, Green Jay, plus 3 <b>lookalike pairs</b>: "
        "Mourning Dove / Rock Dove, Red-tailed / Red-shouldered Hawk, Crow / Common Grackle.",
        "<b>Split:</b> 1,197 training (the model learns), 256 validation (we compare models), 257 test (final check, used once).",
        "<b>Challenges:</b> lookalike birds, only ~120 training photos per bird, and hawks usually have sky behind them.",
    ]),
    ("How we prepared the photos", [
        "<b>Split</b> 70/15/15, same share of each bird in every group. <b>Resize</b> to 224 × 224 (128 × 128 for the baseline, to train faster).",
        "<b>Normalize:</b> scale pixel values 0–255 down to 0–1 (each pretrained model has its own scaling).",
        "<b>Augmentation:</b> random flips, rotations, zoom and contrast on training photos. We tested it, and <b>it didn't help</b>, so the best models don't use it.",
    ]),
    ("The three models", [
        "<b>Baseline CNN:</b> built from scratch. 4 convolution + pooling blocks, dropout, softmax for 10 birds. ~242,000 weights. Adam optimizer, up to 30 epochs.",
        "<b>MobileNetV2:</b> small, fast model already trained on ~1.3 million photos (ImageNet). We used <b>feature extraction</b>: its layers stay "
        "frozen, and we only trained a new last layer for our 10 birds (12,810 weights).",
        "<b>ResNet50:</b> same idea, but a much bigger model (50 layers, ~23.6 million frozen weights). New last layer: 20,490 weights.",
        "We also tried <b>fine-tuning</b> MobileNetV2 (retraining its top layers). It didn't do better, so we kept feature extraction.",
    ]),
    ("The results (257 test photos)", [
        "<b>Baseline CNN: 68.5%</b> correct (loss 0.86, 81 mistakes).",
        "<b>MobileNetV2: 96.1%</b> correct (loss 0.12, 10 mistakes, all between lookalike birds).",
        "<b>ResNet50: 98.1%</b> correct (loss 0.095, 5 mistakes). <b>Our strongest model.</b>",
        "<b>Why ResNet50 won:</b> it's deeper and sees more detail (2,048 features per photo vs. 1,280). <b>Why both pretrained models beat our CNN:</b> "
        "they already learned what feathers, eyes and beaks look like from a million-plus photos.",
        "<b>Heatmaps (Grad-CAM)</b> show the model looks at the bird, not the sky background.",
    ]),
    ("Key words in one line", [
        "<b>CNN:</b> a neural network for images that finds edges, then textures, then shapes.",
        "<b>Transfer learning:</b> reusing a model already trained on a huge photo set. <b>Feature extraction:</b> keep it frozen and train only a new last layer.",
        "<b>Epoch:</b> one pass through all training photos. <b>Loss:</b> how wrong the model is (lower is better). <b>Accuracy:</b> % of photos right.",
        "<b>Overfitting:</b> memorizing the training photos instead of learning; shows up as training scores much higher than validation.",
        "<b>Precision / recall / F1:</b> per bird: how often a guess is right / how many of that bird we found / the balance of the two.",
        "<b>Confusion matrix:</b> a grid of true vs. predicted birds; the diagonal is correct, everything else is a mix-up.",
    ]),
]

RESULTS = [["Model", "How it was used", "Test accuracy", "Test loss", "Mistakes (of 257)"],
           ["Baseline CNN", "Built from scratch", "68.5%", "0.857", "81"],
           ["MobileNetV2", "Feature extraction (frozen)", "96.1%", "0.118", "10"],
           ["ResNet50 (best)", "Feature extraction (frozen)", "98.1%", "0.095", "5"]]

QA = []
