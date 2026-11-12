#!/bin/zsh
set -euo pipefail

for episode in 03 04 05 06 07 08 09 10 11 12 13 14 15; do
  project="thai-alphabet-pinkfong-${episode}-lesson"
  /opt/homebrew/anaconda3/bin/python3 -u scripts/synth_narration.py \
    "$project" --only-lang th \
    > "projects/${project}/artifacts/tts_thai.log" 2>&1
  print "${project}: 泰语发音完成"
done
