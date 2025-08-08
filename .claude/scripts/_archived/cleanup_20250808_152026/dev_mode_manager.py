#!/usr/bin/env python3
"""
Development mode manager
Enables enhanced debugging, logging, and safety features for internal dev teams
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging
import sys

class DevModeManager:
    """Manages development mode configuration and features"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.settings_file = self.claude_dir / 'settings.local.json'
        
        self.setup_logging()
        
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def setup_logging(self):
        """Setup dev mode manager logging"""
        log_dir = self.claude_dir / 'logs' / 'dev_mode'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'dev_mode_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load current settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading settings: {e}")
                return {}
        return {}
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save settings atomically"""
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Atomic replace
            temp_file.replace(self.settings_file)
            
            self.logger.info("Settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            raise
    
    def get_default_dev_config(self) -> Dict[str, Any]:
        """Get default development mode configuration"""
        return {
            "enabled": True,
            "verbose_logging": True,
            "fail_fast": True,
            "debug_hooks": True,
            "resource_monitoring": True,
            "auto_backup": True,
            "confirmation_prompts": True,
            "performance_profiling": True,
            "enhanced_error_reporting": True,
            "command_validation": True,
            "state_monitoring": True
        }
    
    def enable_dev_mode(self):
        """Enable development mode with all debugging features"""
        print("🔧 Enabling development mode...")
        
        settings = self.load_settings()
        
        # Add development mode configuration
        settings["development_mode"] = self.get_default_dev_config()
        
        # Enhanced execution settings
        settings["execution"] = settings.get("execution", {})
        settings["execution"].update({
            "enable_real_execution": True,
            "simulate_mode": False,
            "default_timeout": 600,  # Longer timeouts for debugging
            "agent_timeout": 1200,
            "verbose_output": True
        })
        
        # Enhanced resource monitoring
        settings["resources"] = settings.get("resources", {})
        settings["resources"].update({
            "max_concurrent_tasks": 4,  # Conservative for debugging
            "cpu_limit_percent": 70,    # Conservative limits
            "memory_limit_percent": 60,
            "monitoring_enabled": True,
            "detailed_logging": True
        })
        
        # Enhanced workflow settings
        settings["workflow"] = settings.get("workflow", {})
        settings["workflow"].update({
            "auto_progression": False,  # Manual control in dev mode
            "max_retries": 1,          # Fail fast
            "retry_delay": 2,
            "backup_before_phases": True,
            "confirmation_required": True
        })
        
        # Enhanced hooks
        settings["hooks"] = settings.get("hooks", {})
        settings["hooks"].update({
            "post_command": {
                "enabled": True,
                "script": ".claude/hooks/phase-complete.sh",
                "debug_mode": True
            },
            "pre_task": {
                "enabled": True,
                "script": ".claude/hooks/pre-task.sh",
                "debug_mode": True
            },
            "post_task": {
                "enabled": True,
                "script": ".claude/hooks/post-task.sh",
                "debug_mode": True
            }
        })
        
        # Enhanced logging
        settings["logging"] = settings.get("logging", {})
        settings["logging"].update({
            "level": "DEBUG",
            "detailed_execution": True,
            "agent_performance": True,
            "resource_tracking": True,
            "command_history": True,
            "error_context": True
        })
        
        self.save_settings(settings)
        
        print("✅ Development mode enabled!")
        print("\\n📊 Active features:")
        print("  • Verbose logging and debugging")
        print("  • Enhanced error reporting")
        print("  • Resource monitoring")
        print("  • Automatic backups")
        print("  • Confirmation prompts")
        print("  • Performance profiling")
        print("  • Command validation")
        print("\\n🎯 Next steps:")
        print("  • Run workflows with detailed logging")
        print("  • Use /dashboard for real-time monitoring")
        print("  • Check logs in .claude/logs/ for detailed traces")
        
        self.logger.info("Development mode enabled with full debugging features")
    
    def disable_dev_mode(self):
        """Disable development mode and return to production settings"""
        print("⚡ Disabling development mode...")
        
        settings = self.load_settings()
        
        # Remove or disable development mode
        if "development_mode" in settings:
            settings["development_mode"]["enabled"] = False
        
        # Production execution settings
        settings["execution"] = settings.get("execution", {})
        settings["execution"].update({
            "enable_real_execution": True,
            "simulate_mode": False,
            "default_timeout": 300,
            "agent_timeout": 600,
            "verbose_output": False
        })
        
        # Production resource settings
        settings["resources"] = settings.get("resources", {})
        settings["resources"].update({
            "max_concurrent_tasks": 8,
            "cpu_limit_percent": 80,
            "memory_limit_percent": 75,
            "monitoring_enabled": False,
            "detailed_logging": False
        })
        
        # Production workflow settings
        settings["workflow"] = settings.get("workflow", {})
        settings["workflow"].update({
            "auto_progression": True,
            "max_retries": 3,
            "retry_delay": 5,
            "backup_before_phases": False,
            "confirmation_required": False
        })
        
        # Standard logging
        settings["logging"] = settings.get("logging", {})
        settings["logging"].update({
            "level": "INFO",
            "detailed_execution": False,
            "agent_performance": False,
            "resource_tracking": False,
            "command_history": False,
            "error_context": False
        })
        
        self.save_settings(settings)
        
        print("✅ Development mode disabled!")
        print("\\n🚀 Production settings restored:")
        print("  • Optimized performance")
        print("  • Auto workflow progression")
        print("  • Standard error recovery")
        print("  • Minimal logging overhead")
        
        self.logger.info("Development mode disabled, production settings restored")
    
    def show_status(self):
        """Show current development mode status"""
        settings = self.load_settings()
        dev_config = settings.get("development_mode", {})
        
        is_enabled = dev_config.get("enabled", False)
        
        print(f"🔧 Development Mode: {'ENABLED' if is_enabled else 'DISABLED'}")
        
        if is_enabled:
            print("\\n📊 Active Features:")
            features = [
                ("Verbose Logging", dev_config.get("verbose_logging", False)),
                ("Fail Fast", dev_config.get("fail_fast", False)),
                ("Debug Hooks", dev_config.get("debug_hooks", False)),
                ("Resource Monitoring", dev_config.get("resource_monitoring", False)),
                ("Auto Backup", dev_config.get("auto_backup", False)),
                ("Confirmation Prompts", dev_config.get("confirmation_prompts", False)),
                ("Performance Profiling", dev_config.get("performance_profiling", False)),
                ("Enhanced Error Reporting", dev_config.get("enhanced_error_reporting", False)),
                ("Command Validation", dev_config.get("command_validation", False)),
                ("State Monitoring", dev_config.get("state_monitoring", False))
            ]
            
            for feature, enabled in features:
                status = "✅" if enabled else "❌"
                print(f"  {status} {feature}")
        
        # Show current resource settings
        resources = settings.get("resources", {})
        execution = settings.get("execution", {})
        
        print("\\n⚙️ Current Configuration:")
        print(f"  • Max Concurrent Tasks: {resources.get('max_concurrent_tasks', 8)}")
        print(f"  • CPU Limit: {resources.get('cpu_limit_percent', 80)}%")
        print(f"  • Memory Limit: {resources.get('memory_limit_percent', 75)}%")
        print(f"  • Default Timeout: {execution.get('default_timeout', 300)}s")
        print(f"  • Auto Progression: {settings.get('workflow', {}).get('auto_progression', True)}")
        
        # Show log locations
        print("\\n📁 Log Locations:")
        print(f"  • Execution Logs: {self.claude_dir}/logs/execution/")
        print(f"  • Resource Logs: {self.claude_dir}/logs/resources/")
        print(f"  • State Logs: {self.claude_dir}/logs/state/")
        print(f"  • Dev Mode Logs: {self.claude_dir}/logs/dev_mode/")
    
    def toggle_feature(self, feature_name: str, enabled: bool):
        """Toggle a specific development mode feature"""
        settings = self.load_settings()
        dev_config = settings.get("development_mode", {})
        
        if not dev_config.get("enabled", False):
            print("❌ Development mode is not enabled. Run '/dev-mode on' first.")
            return
        
        if feature_name in dev_config:
            dev_config[feature_name] = enabled
            settings["development_mode"] = dev_config
            self.save_settings(settings)
            
            status = "enabled" if enabled else "disabled"
            print(f"✅ {feature_name} {status}")
        else:
            print(f"❌ Unknown feature: {feature_name}")
            print("Available features:", list(self.get_default_dev_config().keys()))

def main():
    """Main function for development mode management"""
    parser = argparse.ArgumentParser(description='Development Mode Manager')
    parser.add_argument('action', choices=['on', 'off', 'status', 'toggle'], 
                       help='Action to perform')
    parser.add_argument('--feature', help='Feature to toggle (use with toggle action)')
    parser.add_argument('--enable', action='store_true', help='Enable feature (use with toggle)')
    parser.add_argument('--disable', action='store_true', help='Disable feature (use with toggle)')
    
    args = parser.parse_args()
    
    manager = DevModeManager()
    
    if args.action == 'on':
        manager.enable_dev_mode()
    elif args.action == 'off':
        manager.disable_dev_mode()
    elif args.action == 'status':
        manager.show_status()
    elif args.action == 'toggle':
        if not args.feature:
            print("❌ --feature required for toggle action")
            return
        
        if args.enable:
            manager.toggle_feature(args.feature, True)
        elif args.disable:
            manager.toggle_feature(args.feature, False)
        else:
            print("❌ Use --enable or --disable with toggle action")

if __name__ == "__main__":
    main()