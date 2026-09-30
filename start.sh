#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mapfile -t files < <(find . -maxdepth 1 -name '*.py' -printf '%f\n' | sort)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "当前目录没有 .py 文件。"
  exit 1
fi

echo
echo "可运行的 Python 文件:"
for i in "${!files[@]}"; do
  printf "  %d) %s\n" "$((i + 1))" "${files[$i]}"
done
echo

read -r -p "输入编号或文件名: " choice

if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#files[@]} )); then
  target="${files[$((choice - 1))]}"
elif [[ -f "$choice" ]]; then
  target="$choice"
else
  echo "没有这个文件: $choice"
  exit 1
fi

echo
echo "运行 $target"
python "$target"
