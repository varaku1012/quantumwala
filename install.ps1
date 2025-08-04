# Claude Code Multi-Agent System Installer (PowerShell)
# One-line installation: iwr -useb https://your-repo/install.ps1 | iex

param(
    [string]$InstallDir = ".claude",
    [switch]$Force
)

# Colors
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

function Write-Banner {
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║     Claude Code Multi-Agent System Installer v1.0.0      ║" -ForegroundColor Blue
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [version]$matches[1]
            if ($version -ge [version]"3.7") {
                Write-Success "Python $($version) found"
            } else {
                Write-Error "Python $version is too old. Minimum required: 3.7"
                return $false
            }
        } else {
            Write-Error "Could not determine Python version"
            return $false
        }
    } catch {
        Write-Error "Python not found. Please install Python 3.7 or later"
        return $false
    }
    
    # Check Git
    try {
        git --version | Out-Null
        Write-Success "Git found"
    } catch {
        Write-Warning "Git not found. Some features may not work properly"
    }
    
    # Check pip
    try {
        pip --version | Out-Null
        Write-Success "pip found"
    } catch {
        Write-Error "pip not found"
        return $false
    }
    
    return $true
}

function New-DirectoryStructure {
    Write-Step "Setting up directory structure..."
    
    $directories = @(
        "agents", "commands", "steering", "scripts", "specs",
        "context", "hooks", "templates", "logs/sessions",
        "logs/reports", "logs/analysis", "logs/phases",
        "logs/archive", "logs/performance", "system-docs",
        "tests", "docs"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $InstallDir $dir
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
    
    Write-Success "Directory structure created"
}

function Install-CoreFiles {
    Write-Step "Installing core system files..."
    
    # Create version file
    "1.0.0" | Out-File -FilePath (Join-Path $InstallDir "VERSION") -Encoding utf8
    
    # Create system info
    $systemInfo = @{
        name = "Claude Code Multi-Agent System"
        version = "1.0.0"
        installed = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        components = @{
            agents = "1.0.0"
            commands = "1.0.0"
            scripts = "1.0.0"
            dashboard = "1.0.0"
            performance = "1.0.0"
        }
    } | ConvertTo-Json -Depth 3
    
    $systemInfo | Out-File -FilePath (Join-Path $InstallDir "system-info.json") -Encoding utf8
    
    Write-Success "Core files installed"
}

function Install-Dependencies {
    Write-Step "Installing Python dependencies..."
    
    $requirements = "psutil>=5.9.0"
    $requirements | Out-File -FilePath (Join-Path $InstallDir "requirements.txt") -Encoding utf8
    
    try {
        pip install -q -r (Join-Path $InstallDir "requirements.txt")
        Write-Success "Dependencies installed"
    } catch {
        Write-Warning "Could not install some dependencies. System may still work."
    }
}

function Initialize-Configuration {
    Write-Step "Initializing configuration..."
    
    # Create spec-config.json
    $specConfig = @{
        spec_workflow = @{
            version = "1.0.0"
            auto_create_directories = $true
            auto_reference_requirements = $true
            enforce_approval_workflow = $true
            default_feature_prefix = "feature-"
            supported_formats = @("markdown", "mermaid")
            agents_enabled = $true
            context_engineering = $true
        }
        context_settings = @{
            max_tokens_per_load = 5000
            smart_loading = $true
            cross_platform = $true
        }
    } | ConvertTo-Json -Depth 3
    
    $specConfig | Out-File -FilePath (Join-Path $InstallDir "spec-config.json") -Encoding utf8
    
    # Create project-state.json
    $projectState = @{
        project = @{
            name = "Your Project Name"
            description = "Your project description"
            created = (Get-Date).ToString("yyyy-MM-dd")
            phase = "setup_complete"
        }
        steering = @{
            initialized = $false
            documents = @{
                product = $false
                tech = $false
                structure = $false
            }
        }
        phases = @{
            setup = @{
                status = "complete"
                timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            }
        }
    } | ConvertTo-Json -Depth 3
    
    $projectState | Out-File -FilePath (Join-Path $InstallDir "project-state.json") -Encoding utf8
    
    Write-Success "Configuration initialized"
}

function New-SteeringTemplates {
    Write-Step "Creating steering document templates..."
    
    # Product template
    $productTemplate = @"
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
"@
    
    $productTemplate | Out-File -FilePath (Join-Path $InstallDir "steering/product.md") -Encoding utf8
    
    # Tech template
    $techTemplate = @"
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
"@
    
    $techTemplate | Out-File -FilePath (Join-Path $InstallDir "steering/tech.md") -Encoding utf8
    
    # Structure template
    $structureTemplate = @"
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
"@
    
    $structureTemplate | Out-File -FilePath (Join-Path $InstallDir "steering/structure.md") -Encoding utf8
    
    Write-Success "Steering templates created"
}

function New-ClaudeMd {
    $claudeMd = @"
# Claude Code Multi-Agent Development System

This project uses an enhanced multi-agent workflow system with Claude Code.

## Quick Start

1. **Initialize steering context:**
   ``````
   /steering-setup
   ``````

2. **Create a feature:**
   ``````
   /spec-create "feature-name" "description"
   ``````

3. **Generate tasks:**
   ``````
   /spec-generate-tasks feature-name
   ``````

4. **View dashboard:**
   ``````
   /dashboard enhanced
   ``````

## Installation Info

- **Version**: 1.0.0
- **Installed**: $((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))
- **Location**: $InstallDir/

## Available Commands

Run ``/help`` to see all available agents and commands.

## Uninstall

To remove the system, run:
``````
./$InstallDir/uninstall.ps1
``````
"@
    
    $claudeMd | Out-File -FilePath "CLAUDE.md" -Encoding utf8
}

function New-UninstallScript {
    $uninstallScript = @"
# Uninstall Claude Code Multi-Agent System

Write-Host "This will remove the Claude Code Multi-Agent System." -ForegroundColor Yellow
`$response = Read-Host "Are you sure? (y/N)"
if (`$response -eq "y" -or `$response -eq "Y") {
    Remove-Item -Recurse -Force ".claude" -ErrorAction SilentlyContinue
    Remove-Item -Force "CLAUDE.md" -ErrorAction SilentlyContinue
    Write-Host "Claude Code Multi-Agent System has been removed." -ForegroundColor Green
} else {
    Write-Host "Uninstall cancelled." -ForegroundColor Blue
}
"@
    
    $uninstallScript | Out-File -FilePath (Join-Path $InstallDir "uninstall.ps1") -Encoding utf8
}

function Test-Installation {
    Write-Step "Running verification tests..."
    
    $directories = @("agents", "commands", "scripts", "steering")
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $InstallDir $dir
        if (Test-Path $fullPath) {
            Write-Success "$dir directory verified"
        } else {
            Write-Error "$dir directory missing"
            return $false
        }
    }
    
    return $true
}

function Main {
    Write-Banner
    
    # Check if installation directory exists
    if (Test-Path $InstallDir) {
        if (-not $Force) {
            Write-Warning "Directory $InstallDir already exists"
            $response = Read-Host "Do you want to overwrite it? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                Write-Error "Installation cancelled"
                exit 1
            }
        }
        Remove-Item -Recurse -Force $InstallDir
    }
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites check failed"
        exit 1
    }
    
    # Create installation directory
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    
    # Setup directories
    New-DirectoryStructure
    
    # Install core files
    Install-CoreFiles
    
    # Install dependencies
    Install-Dependencies
    
    # Initialize configuration
    Initialize-Configuration
    
    # Create steering templates
    New-SteeringTemplates
    
    # Create uninstall script
    New-UninstallScript
    
    # Create CLAUDE.md
    New-ClaudeMd
    
    # Run verification
    if (-not (Test-Installation)) {
        Write-Error "Verification failed"
        exit 1
    }
    
    # Success message
    Write-Host ""
    Write-Success "Installation completed successfully!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Edit steering documents in $InstallDir/steering/"
    Write-Host "2. Run /steering-setup in Claude Code"
    Write-Host "3. Create your first feature with /spec-create"
    Write-Host ""
    Write-Host "Happy coding with Claude Code Multi-Agent System!" -ForegroundColor Blue
}

# Run main function
Main