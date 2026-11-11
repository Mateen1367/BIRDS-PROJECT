# Birds of Texas: Classifying 10 Bird Species with CNNs

DATA 4380 (Data Problems) computer vision project · Alejandro Alfonso, Tej Govindu, Mateen Jan

**Question:** Can a convolutional neural network identify 10 common Texas bird species from a photo, including lookalike pairs (two doves, two hawks, crow vs. grackle)?

## Data
- Source: *BIRDS 525 Species – Image Classification* (G. Piosenka, Kaggle). The Kaggle page has been removed; we use the CC0 mirror at [huggingface.co/datasets/chriamue/bird-species-dataset](https://huggingface.co/datasets/chriamue/bird-species-dataset).
- 10 species, ~1,700 images, 224×224 RGB, one cropped bird per image.
- The original test set has only 5 images per species, so we pool all images and make our own stratified 70/15/15 train/validation/test split.

| Easy | Lookalike pairs |
|---|---|
| Northern Cardinal, Northern Mockingbird, Roadrunner, Green Jay | Mourning Dove / Rock Dove · Red-tailed / Red-shouldered Hawk · Crow / Common Grackle |

## Repo layout
```
data/            raw download (git-ignored) and processed split lists
notebooks/       01_data_and_preprocessing, 02_modeling_and_evaluation
src/             download_data.sh and helper code
reports/         slides, speaker notes, figures
docs/            presentation plan and references
```

## Reproduce
```bash
pip install -r requirements.txt
bash src/download_data.sh
```
Then run the notebooks in order.

## Results
_Coming soon._
