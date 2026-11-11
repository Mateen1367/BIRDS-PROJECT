#!/usr/bin/env bash
# Downloads BIRDS 525 (CC0 mirror on Hugging Face) and keeps only our 10 Texas species.
# Run from the repo root:  bash src/download_data.sh
set -e
mkdir -p data/raw && cd data/raw
B=https://huggingface.co/datasets/chriamue/bird-species-dataset/resolve/main/data
curl -sL -o birds.csv "$B/birds.csv"
PATS=()
for s in "NORTHERN CARDINAL" "NORTHERN MOCKINGBIRD" "ROADRUNNER" "GREEN JAY" "MOURNING DOVE" \
         "ROCK DOVE" "RED TAILED HAWK" "RED SHOULDERED HAWK" "CROW" "COMMON GRACKLE"; do
  PATS+=("*/$s/*")
done
for f in valid test train; do
  curl -sL "$B/$f.tar.gz" | tar -xz --wildcards --no-anchored "${PATS[@]}"
done
echo "done: $(find . -name '*.jpg' | wc -l) images"
