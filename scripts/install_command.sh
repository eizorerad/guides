#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "$0")/.." && pwd)
pixi_bin=$(command -v pixi)
launcher_dir="${XDG_BIN_HOME:-$HOME/.local/bin}"
launcher="$launcher_dir/guides"
mkdir -p "$launcher_dir"
if [ -e "$launcher" ]; then
    echo "Already exists: $launcher. Use pixi run guides from the project instead."
    exit 1
fi
printf '#!/usr/bin/env bash\nexec %q run --manifest-path %q python -m guides "$@"\n' \
    "$pixi_bin" "$project_dir/pixi.toml" > "$launcher"
chmod +x "$launcher"
echo "Installed $launcher (keep this project directory in place)."
