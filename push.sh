#!/bin/zsh
# 📟 ARCHITECT PUSH PROTOCOL (v1.0) - Linux/Zsh Version
# Purpose: Syncs only lean logic to GitHub & Vercel.

commitMsg=$1
if [ -z "$commitMsg" ]; then
    commitMsg="chore: automated sync [Lean Mode]"
fi

# Colors for Zsh
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
WHITE='\033[1;37m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Starting Deployment Sync...${NC}"

# 1. Verification of Lean Git
echo -e "${YELLOW}📦 Cleaning context killers...${NC}"
git add .
git status

# 2. Local Commit
echo -e "${GREEN}💾 Committing logic...${NC}"
git commit -m "$commitMsg"

# 3. Remote Sync
echo -e "${BLUE}🌍 Pushing to GitHub (main)...${NC}"
git push origin main

# 4. Success Signal
echo -e "${WHITE}✅ Lean logic synced to: https://github.com/SrAndres629/web-y-tracking-supabase-jorge${NC}"
echo -e "${MAGENTA}⚡ Vercel Deployment should trigger automatically.${NC}"
