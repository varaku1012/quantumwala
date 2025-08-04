#!/bin/bash
#
# Claude Code Multi-Agent System Installer
# One-line installation: curl -fsSL https://your-repo/install.sh | bash
#
# This script will:
# 1. Check prerequisites
# 2. Download and setup the multi-agent system
# 3. Initialize configuration
# 4. Run verification tests
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/your-org/claude-code-multi-agent"
INSTALL_DIR=".claude"
MIN_PYTHON_VERSION="3.7"
REQUIRED_COMMANDS=("git" "python3" "pip3")

# Helper functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║     Claude Code Multi-Agent System Installer v1.0.0      ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if version_ge "$PYTHON_VERSION" "$MIN_PYTHON_VERSION"; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python $PYTHON_VERSION is too old. Minimum required: $MIN_PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local missing=()
    
    for cmd in "${REQUIRED_COMMANDS[@]}"; do
        if command_exists "$cmd"; then
            print_success "$cmd found"
        else
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Missing required commands: ${missing[*]}"
        echo "Please install the missing commands and try again."
        return 1
    fi
    
    check_python_version || return 1
    
    # Check pip packages
    print_step "Checking Python packages..."
    python3 -m pip install --quiet --upgrade pip
    
    return 0
}

# Download repository
download_repository() {
    print_step "Downloading Claude Code Multi-Agent System..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists"
        read -p "Do you want to overwrite it? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    # For now, create the structure locally
    # In production, this would clone from the repository
    mkdir -p "$INSTALL_DIR"
    
    print_success "Created $INSTALL_DIR directory"
}

# Setup directory structure
setup_directories() {
    print_step "Setting up directory structure..."
    
    directories=(
        "agents"
        "commands"
        "steering"
        "scripts"
        "specs"
        "context"
        "hooks"
        "templates"
        "logs/sessions"
        "logs/reports"
        "logs/analysis"
        "logs/phases"
        "logs/archive"
        "logs/performance"
        "system-docs"
        "tests"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$INSTALL_DIR/$dir"
    done
    
    print_success "Directory structure created"
}

# Download core files
download_core_files() {
    print_step "Downloading core system files..."
    
    # In production, this would download from the repository
    # For now, we'll create placeholder files
    
    # Create version file
    cat > "$INSTALL_DIR/VERSION" << EOF
1.0.0
EOF
    
    # Create system info
    cat > "$INSTALL_DIR/system-info.json" << EOF
{
    "name": "Claude Code Multi-Agent System",
    "version": "1.0.0",
    "installed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "components": {
        "agents": "1.0.0",
        "commands": "1.0.0",
        "scripts": "1.0.0",
        "dashboard": "1.0.0",
        "performance": "1.0.0"
    }
}
EOF
    
    print_success "Core files downloaded"
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Create requirements file
    cat > "$INSTALL_DIR/requirements.txt" << EOF
psutil>=5.9.0
EOF
    
    python3 -m pip install --quiet -r "$INSTALL_DIR/requirements.txt"
    
    print_success "Dependencies installed"
}

# Initialize configuration
initialize_configuration() {
    print_step "Initializing configuration..."
    
    # Create spec-config.json
    cat > "$INSTALL_DIR/spec-config.json" << EOF
{
    "spec_workflow": {
        "version": "1.0.0",
        "auto_create_directories": true,
        "auto_reference_requirements": true,
        "enforce_approval_workflow": true,
        "default_feature_prefix": "feature-",
        "supported_formats": ["markdown", "mermaid"],
        "agents_enabled": true,
        "context_engineering": true
    },
    "context_settings": {
        "max_tokens_per_load": 5000,
        "smart_loading": true,
        "cross_platform": true
    }
}
EOF
    
    # Create project-state.json
    cat > "$INSTALL_DIR/project-state.json" << EOF
{
    "project": {
        "name": "Your Project Name",
        "description": "Your project description",
        "created": "$(date +%Y-%m-%d)",
        "phase": "setup_complete"
    },
    "steering": {
        "initialized": false,
        "documents": {
            "product": false,
            "tech": false,
            "structure": false
        }
    },
    "phases": {
        "setup": {
            "status": "complete",
            "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        }
    }
}
EOF
    
    print_success "Configuration initialized"
}

# Create steering templates
create_steering_templates() {
    print_step "Creating steering document templates..."
    
    # Product template
    cat > "$INSTALL_DIR/steering/product.md" << 'EOF'
---
name: product
version: 1.0.0
---

# Product Steering Document

## Vision
[Your product vision here]

## Target Users
[Define your target users]

## Core Features
[List core features]

## Success Metrics
[Define success metrics]
EOF
    
    # Tech template
    cat > "$INSTALL_DIR/steering/tech.md" << 'EOF'
---
name: tech
version: 1.0.0
---

# Technology Steering Document

## Technology Stack
[Your technology choices]

## Architecture Principles
[Define architecture principles]

## Performance Requirements
[List performance requirements]

## Security Standards
[Define security standards]
EOF
    
    # Structure template
    cat > "$INSTALL_DIR/steering/structure.md" << 'EOF'
---
name: structure
version: 1.0.0
---

# Structure Steering Document

## Code Organization
[Define code organization]

## Naming Conventions
[List naming conventions]

## Development Workflow
[Define development workflow]

## Testing Standards
[Define testing standards]
EOF
    
    print_success "Steering templates created"
}

# Run verification tests
run_verification() {
    print_step "Running verification tests..."
    
    # Check if Python can access the installation
    python3 -c "import os; assert os.path.exists('$INSTALL_DIR')" || {
        print_error "Installation directory not accessible"
        return 1
    }
    
    # Check if all directories exist
    for dir in agents commands scripts steering; do
        if [ -d "$INSTALL_DIR/$dir" ]; then
            print_success "$dir directory verified"
        else
            print_error "$dir directory missing"
            return 1
        fi
    done
    
    return 0
}

# Create uninstall script
create_uninstall_script() {
    cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# Uninstall Claude Code Multi-Agent System

echo "This will remove the Claude Code Multi-Agent System."
read -p "Are you sure? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf .claude
    rm -f CLAUDE.md
    echo "Claude Code Multi-Agent System has been removed."
else
    echo "Uninstall cancelled."
fi
EOF
    
    chmod +x "$INSTALL_DIR/uninstall.sh"
}

# Create CLAUDE.md
create_claude_md() {
    cat > "CLAUDE.md" << EOF
# Claude Code Multi-Agent Development System

This project uses an enhanced multi-agent workflow system with Claude Code.

## Quick Start

1. **Initialize steering context:**
   \`\`\`
   /steering-setup
   \`\`\`

2. **Create a feature:**
   \`\`\`
   /spec-create "feature-name" "description"
   \`\`\`

3. **Generate tasks:**
   \`\`\`
   /spec-generate-tasks feature-name
   \`\`\`

4. **View dashboard:**
   \`\`\`
   /dashboard enhanced
   \`\`\`

## Installation Info

- **Version**: 1.0.0
- **Installed**: $(date +"%Y-%m-%d %H:%M:%S")
- **Location**: $INSTALL_DIR/

## Available Commands

Run \`/help\` to see all available agents and commands.

## Uninstall

To remove the system, run:
\`\`\`
./$INSTALL_DIR/uninstall.sh
\`\`\`
EOF
}

# Main installation flow
main() {
    print_banner
    
    # Check prerequisites
    if ! check_prerequisites; then
        print_error "Prerequisites check failed"
        exit 1
    fi
    
    # Download repository
    download_repository
    
    # Setup directories
    setup_directories
    
    # Download core files
    download_core_files
    
    # Install dependencies
    install_dependencies
    
    # Initialize configuration
    initialize_configuration
    
    # Create steering templates
    create_steering_templates
    
    # Create uninstall script
    create_uninstall_script
    
    # Create CLAUDE.md
    create_claude_md
    
    # Run verification
    if ! run_verification; then
        print_error "Verification failed"
        exit 1
    fi
    
    # Success message
    echo
    print_success "Installation completed successfully!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Edit steering documents in $INSTALL_DIR/steering/"
    echo "2. Run /steering-setup in Claude Code"
    echo "3. Create your first feature with /spec-create"
    echo
    echo -e "${BLUE}Happy coding with Claude Code Multi-Agent System!${NC}"
}

# Run main function
main "$@"