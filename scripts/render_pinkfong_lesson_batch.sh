#!/bin/zsh
set -euo pipefail

for episode in 02 03 04 05 06 07 08 09 10 11 12 13 14 15; do
  project="thai-alphabet-pinkfong-${episode}-lesson"
  output_name="final_v2"
  if [[ -s "projects/${project}/renders/${output_name}.mp4" ]]; then
    print "${project}: 已有新版成片，跳过"
    continue
  fi
  /opt/homebrew/anaconda3/bin/python3 -u scripts/atelier_render.py \
    "$project" PinkfongAlphabetLesson "$output_name" --use-existing \
    > "projects/${project}/artifacts/render_v2.log" 2>&1
  print "${project}: 成片完成"
done
