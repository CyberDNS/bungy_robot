#!/bin/bash
# Upload the working tree to the robot (Raspberry Pi) for quick testing.
# Usage: ./deploy.sh [--build] [--prune] [--dry-run]
#   --build    also run ./build.sh pi on the robot after uploading
#   --prune    also delete files on the robot that no longer exist here
#              (check with --dry-run first)
#   --dry-run  show what would change, upload nothing
# Settings come from the git-ignored bungy.env.local (see bungy.env.example).

set -e
cd "$(dirname "$0")"

if [ ! -f bungy.env.local ]; then
    echo "bungy.env.local not found. Run: cp bungy.env.example bungy.env.local" >&2
    exit 1
fi
set -a; source bungy.env.local; set +a

TARGET="${ROBOT_SSH_HOST:-${ROBOT_USER:+$ROBOT_USER@}$ROBOT_IP}"
REMOTE_DIR="${ROBOT_REPO_DIR:-repos/bungy_robot}"   # relative to the robot user's home
if [ -z "$TARGET" ]; then echo "Set ROBOT_SSH_HOST or ROBOT_IP in bungy.env.local" >&2; exit 1; fi

BUILD=false; DRY=(); PRUNE=()
for arg in "$@"; do
    case "$arg" in
        --build) BUILD=true ;;
        --prune) PRUNE=(--delete) ;;
        --dry-run) DRY=(--dry-run --itemize-changes) ;;
        -h|--help) sed -n 2,11p "$0"; exit 0 ;;
        *) echo "Unknown option: $arg" >&2; exit 1 ;;
    esac
done

echo "Deploying to $TARGET:~/$REMOTE_DIR"
# Build artifacts, git data and the local env file are never uploaded or pruned.
rsync -a "${PRUNE[@]}" "${DRY[@]}" \
    --exclude .git --exclude 'build/' --exclude 'install/' --exclude 'log/' \
    --exclude 'bungy.env.local' --exclude '__pycache__/' \
    ./ "$TARGET:$REMOTE_DIR/"

if $BUILD && [ ${#DRY[@]} -eq 0 ]; then
    echo "Building on the robot..."
    ssh "$TARGET" "cd $REMOTE_DIR && ./build.sh pi"
fi
echo "Done."
