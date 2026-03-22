#!/bin/bash
# =============================================================================
# Deploy ROS2 packages from workstation to the Rosmaster X3 Plus
#
# Usage:
#   ./scripts/deploy.sh              # Deploy all packages in src/
#   ./scripts/deploy.sh my_package   # Deploy a specific package
# =============================================================================

set -euo pipefail

ROBOT_HOST="x3"  # SSH config alias
ROBOT_WS="/home/jetson/workspaces/x3plus_ws"
LOCAL_WS="$HOME/Workspaces/x3_plus"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Deploying to Rosmaster X3 Plus (${ROBOT_HOST})${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"

# Determine what to deploy
if [ -n "${1:-}" ]; then
    DEPLOY_PATH="$LOCAL_WS/src/$1"
    if [ ! -d "$DEPLOY_PATH" ]; then
        echo -e "${YELLOW}ERROR: Package directory not found: $DEPLOY_PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}► Deploying package: $1${NC}"
    rsync -avz --delete \
        --exclude '.git' \
        --exclude 'build/' \
        --exclude 'install/' \
        --exclude 'log/' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        "$DEPLOY_PATH/" "$ROBOT_HOST:$ROBOT_WS/src/$1/"
else
    echo -e "${GREEN}► Deploying all packages from src/${NC}"
    rsync -avz --delete \
        --exclude '.git' \
        --exclude 'build/' \
        --exclude 'install/' \
        --exclude 'log/' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        "$LOCAL_WS/src/" "$ROBOT_HOST:$ROBOT_WS/src/"
fi

echo ""
echo -e "${GREEN}► Building on robot...${NC}"
ssh "$ROBOT_HOST" "source /opt/ros/humble/setup.bash && cd $ROBOT_WS && colcon build --symlink-install 2>&1 | tail -20"

echo ""
echo -e "${GREEN}✓ Deploy complete!${NC}"
echo -e "${CYAN}  To run on robot:  ssh $ROBOT_HOST${NC}"
echo -e "${CYAN}  Source workspace: source $ROBOT_WS/install/setup.bash${NC}"
