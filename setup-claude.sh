#!/bin/bash

# Claude Code AITK Setup Script (Multilingual Support)
# This script creates symbolic links from your AITK project to ~/.claude/
# so that Claude Code can automatically discover your skills and commands.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "linux"
    fi
}

OS_TYPE=$(detect_os)

# Default language
LANG_CODE="en"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --lang=*)
            LANG_CODE="${1#*=}"
            shift
            ;;
        --lang)
            LANG_CODE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --lang=LANG, --lang LANG    Set language (en or zh-cn, default: en)"
            echo "  -h, --help                  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Use default language (en)"
            echo "  $0 --lang=zh-cn     # Use Chinese"
            echo "  $0 --lang en        # Use English"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate language code
if [[ "$LANG_CODE" != "en" && "$LANG_CODE" != "zh-cn" ]]; then
    echo -e "${RED}Error: Unsupported language '$LANG_CODE'${NC}"
    echo "Supported languages: en, zh-cn"
    exit 1
fi

# Get the absolute path of this script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AITK_DIR="$SCRIPT_DIR"

# Source directories (with language)
AITK_SKILLS_DIR="$AITK_DIR/skills/$LANG_CODE"
AITK_COMMANDS_DIR="$AITK_DIR/commands/$LANG_CODE"

# Target directories
CLAUDE_DIR="$HOME/.claude"
CLAUDE_SKILLS_DIR="$CLAUDE_DIR/skills"
CLAUDE_COMMANDS_DIR="$CLAUDE_DIR/commands"

# Verify source directories exist
if [ ! -d "$AITK_SKILLS_DIR" ]; then
    echo -e "${RED}Error: Skills directory not found: $AITK_SKILLS_DIR${NC}"
    echo "Available languages:"
    ls -d "$AITK_DIR/skills/"*/ 2>/dev/null | xargs -n 1 basename
    exit 1
fi

if [ ! -d "$AITK_COMMANDS_DIR" ]; then
    echo -e "${RED}Error: Commands directory not found: $AITK_COMMANDS_DIR${NC}"
    echo "Available languages:"
    ls -d "$AITK_DIR/commands/"*/ 2>/dev/null | xargs -n 1 basename
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AITK Claude Code Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}OS Detected:${NC} $OS_TYPE"
echo -e "${GREEN}Language:${NC} $LANG_CODE"
echo -e "${GREEN}Source:${NC}"
echo "  Skills: $AITK_SKILLS_DIR"
echo "  Commands: $AITK_COMMANDS_DIR"
echo -e "${GREEN}Target:${NC}"
echo "  Claude: $CLAUDE_DIR/"
echo ""

# Windows-specific warnings
if [ "$OS_TYPE" = "windows" ]; then
    echo -e "${YELLOW}⚠ Windows Detected${NC}"
    echo -e "${YELLOW}Note: On Windows, files will be copied instead of linked.${NC}"
    echo -e "${YELLOW}You'll need to re-run this script after making changes to skills/commands.${NC}"
    echo -e ""
fi

# Function to create directory if it doesn't exist
create_dir() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}Creating directory:${NC} $dir"
        mkdir -p "$dir"
    else
        echo -e "${GREEN}Directory exists:${NC} $dir"
    fi
}

# Function to create or update symlink
create_symlink() {
    local source=$1
    local target=$2
    local name=$3

    if [ "$OS_TYPE" = "windows" ]; then
        # Windows: always remove and re-copy to ensure latest version
        if [ -e "$target" ]; then
            echo -e "${YELLOW}⟳${NC} $name (updating)"
            rm -rf "$target"
        else
            echo -e "${GREEN}+${NC} $name (copying)"
        fi
        if [ -d "$source" ]; then
            cp -r "$source" "$target" && echo -e "${GREEN}  Copied directory${NC}" || echo -e "${RED}  Failed to copy directory${NC}"
        else
            cp "$source" "$target" && echo -e "${GREEN}  Copied file${NC}" || echo -e "${RED}  Failed to copy file${NC}"
        fi
    else
        # Unix/Mac: use symbolic links
        if [ -L "$target" ]; then
            local current_target=$(readlink "$target")
            if [ "$current_target" = "$source" ]; then
                echo -e "${GREEN}✓${NC} $name (already linked)"
            else
                echo -e "${YELLOW}⟳${NC} $name (updating link)"
                rm "$target"
                ln -s "$source" "$target"
            fi
        elif [ -e "$target" ]; then
            echo -e "${RED}✗${NC} $name (conflict: target exists and is not a symlink)"
            echo -e "${YELLOW}  Please manually remove or backup:${NC} $target"
            return 1
        else
            echo -e "${GREEN}+${NC} $name (creating link)"
            ln -s "$source" "$target"
        fi
    fi
}

# Step 1: Create Claude directories
echo -e "\n${BLUE}Step 1: Creating Claude directories${NC}"
create_dir "$CLAUDE_DIR"
create_dir "$CLAUDE_SKILLS_DIR"
create_dir "$CLAUDE_COMMANDS_DIR"

# Step 2: Link skills
echo -e "\n${BLUE}Step 2: Linking skills${NC}"

shopt -s nullglob
SKILL_DIRS=("$AITK_SKILLS_DIR"/*/)
shopt -u nullglob

if [ ${#SKILL_DIRS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No skill directories found in $AITK_SKILLS_DIR${NC}"
else
    for skill_dir in "${SKILL_DIRS[@]}"; do
        skill_name=$(basename "$skill_dir")
        target_dir="$CLAUDE_SKILLS_DIR/$skill_name"

        # If the target is a symlink (old behavior), remove it so we can create a directory
        if [ -L "$target_dir" ]; then
            echo -e "${YELLOW}⟳${NC} Converting $skill_name from symlink to directory structure"
            rm "$target_dir"
        fi

        # Create the skill directory in .claude
        create_dir "$target_dir"

        # Link content from the language-specific directory
        shopt -s nullglob
        skill_files=("$skill_dir"*)
        shopt -u nullglob

        for skill_file in "${skill_files[@]}"; do
            file_name=$(basename "$skill_file")
            create_symlink "$skill_file" "$target_dir/$file_name" "$skill_name/$file_name"
        done

        # Check if there are shared scripts for this skill
        shared_scripts_dir="$AITK_DIR/skills/scripts/$skill_name"
        if [ -d "$shared_scripts_dir" ]; then
            target_scripts_dir="$target_dir/scripts"
            echo -e "${GREEN}  └─${NC} Found shared scripts for $skill_name"
            create_symlink "$shared_scripts_dir" "$target_scripts_dir" "$skill_name/scripts"
        fi
    done
fi

# Step 3: Link commands
echo -e "\n${BLUE}Step 3: Linking commands${NC}"

shopt -s nullglob
COMMAND_FILES=("$AITK_COMMANDS_DIR"/*.md)
shopt -u nullglob

if [ ${#COMMAND_FILES[@]} -eq 0 ]; then
    echo -e "${YELLOW}No command files found in $AITK_COMMANDS_DIR${NC}"
else
    for command_file in "${COMMAND_FILES[@]}"; do
        command_name=$(basename "$command_file")
        target_file="$CLAUDE_COMMANDS_DIR/$command_name"
        create_symlink "$command_file" "$target_file" "$command_name"
    done
fi

# Step 4: Verification
echo -e "\n${BLUE}Step 4: Verification${NC}"

echo -e "\n${YELLOW}Skills in ~/.claude/skills/:${NC}"
if [ -d "$CLAUDE_SKILLS_DIR" ]; then
    skill_count=$(ls -lh "$CLAUDE_SKILLS_DIR" 2>/dev/null | grep -E "^l" | wc -l | tr -d ' ')
    if [ "$skill_count" -eq 0 ]; then
        echo -e "${YELLOW}  No skills linked${NC}"
    else
        ls -lh "$CLAUDE_SKILLS_DIR" | grep -E "^l" | awk '{print "  " $9 " -> " $11}'
    fi
else
    echo -e "${RED}  No skills directory${NC}"
fi

echo -e "\n${YELLOW}Commands in ~/.claude/commands/:${NC}"
if [ -d "$CLAUDE_COMMANDS_DIR" ]; then
    command_count=$(ls -lh "$CLAUDE_COMMANDS_DIR" 2>/dev/null | grep -E "^l" | wc -l | tr -d ' ')
    if [ "$command_count" -eq 0 ]; then
        echo -e "${YELLOW}  No commands linked${NC}"
    else
        ls -lh "$CLAUDE_COMMANDS_DIR" | grep -E "^l" | awk '{print "  " $9 " -> " $11}'
    fi
else
    echo -e "${RED}  No commands directory${NC}"
fi

# Step 5: Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Language: $LANG_CODE"
echo "  Skills linked: $(ls -lh "$CLAUDE_SKILLS_DIR" 2>/dev/null | grep -E "^l" | wc -l | tr -d ' ')"
echo "  Commands linked: $(ls -lh "$CLAUDE_COMMANDS_DIR" 2>/dev/null | grep -E "^l" | wc -l | tr -d ' ')"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Claude Code will now automatically discover these skills"
echo "2. Skills are automatically loaded when needed"
echo ""
echo -e "${YELLOW}Important notes:${NC}"
if [ "$OS_TYPE" = "windows" ]; then
    echo "- ${RED}Windows: Files are copied, not linked. Re-run this script after making changes!${NC}"
    echo "- To remove: ${RED}rm -rf ~/.claude/skills/* ~/.claude/commands/*${NC}"
else
    echo "- Changes to skills/commands in your project are immediately available"
    echo "- To remove links: ${RED}rm ~/.claude/skills/* ~/.claude/commands/*${NC}"
fi
echo "- To switch language, run: ${BLUE}$0 --lang=<lang>${NC}"
echo ""
echo -e "${GREEN}Available languages:${NC}"
ls -d "$AITK_DIR/skills/"*/ 2>/dev/null | xargs -n 1 basename | sed 's/^/  - /'
echo ""
echo -e "${GREEN}Documentation:${NC}"
echo "- Project README: $AITK_DIR/README.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
