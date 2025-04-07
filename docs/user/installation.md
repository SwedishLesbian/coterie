# Grapevine 4.0 Installation Guide

## System Requirements

### Minimum Requirements
- Operating System: Windows 10, macOS 10.14+, or Linux
- RAM: 4GB
- Storage: 500MB free space
- Display: 1280x720 resolution
- Internet: Required for installation only

### Recommended Requirements
- Operating System: Windows 11, macOS 12+, or Ubuntu 22.04
- RAM: 8GB
- Storage: 1GB free space
- Display: 1920x1080 resolution
- Internet: Broadband connection

## Installation Methods

### Windows Installation

#### Using Installer (Recommended)
1. Download the Grapevine-4.0-Setup.exe from the releases page
2. Run the installer
3. Follow the installation wizard
4. Launch Grapevine from the Start Menu

#### Manual Installation
1. Install Python 3.8 or higher from python.org
2. Download Grapevine-4.0.zip
3. Extract to desired location
4. Open command prompt in extracted folder
5. Run: `pip install -r requirements.txt`
6. Run: `python -m grapevine`

### macOS Installation

#### Using DMG (Recommended)
1. Download Grapevine-4.0.dmg
2. Mount the DMG file
3. Drag Grapevine to Applications
4. Launch from Applications folder

#### Using Homebrew
```bash
brew install python
brew install grapevine
```

#### Manual Installation
1. Install Python using Homebrew: `brew install python`
2. Download and extract Grapevine-4.0.tar.gz
3. Open Terminal in extracted folder
4. Run: `pip3 install -r requirements.txt`
5. Run: `python3 -m grapevine`

### Linux Installation

#### Using Package Manager
##### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pip
pip3 install grapevine
```

##### Fedora
```bash
sudo dnf install python3-pip
pip3 install grapevine
```

#### Manual Installation
1. Install Python and pip:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Download and extract Grapevine-4.0.tar.gz
3. Navigate to extracted folder
4. Run: `pip3 install -r requirements.txt`
5. Run: `python3 -m grapevine`

## First-Time Setup

### Database Configuration
1. Launch Grapevine
2. Choose database location when prompted
3. Wait for initial database creation
4. Create admin account if requested

### Application Settings
1. Open Settings from the menu
2. Configure theme (light/dark)
3. Set default save location
4. Adjust UI preferences

## Troubleshooting

### Common Issues

#### Database Connection Error
- Verify database location is accessible
- Check file permissions
- Ensure SQLite is not locked by another process

#### Missing Dependencies
- Run: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify PyQt6 installation

#### Display Issues
- Update graphics drivers
- Check display resolution
- Verify Qt platform plugin

### Error Messages

#### "Failed to create database"
- Check write permissions
- Verify disk space
- Close other database connections

#### "Unable to load UI components"
- Reinstall PyQt6
- Update graphics drivers
- Check Python environment

## Updating

### Automatic Updates
1. Launch Grapevine
2. Accept update prompt
3. Wait for download and installation
4. Restart application

### Manual Updates
1. Download new version
2. Install over existing version
3. Run database migrations if prompted
4. Verify settings preserved

## Uninstallation

### Windows
1. Use Control Panel > Programs
2. Select Grapevine
3. Click Uninstall
4. Delete remaining data if desired

### macOS
1. Delete from Applications
2. Remove ~/Library/Application Support/Grapevine
3. Remove preferences if desired

### Linux
```bash
pip3 uninstall grapevine
rm -rf ~/.config/grapevine
```

## Support

### Getting Help
- Visit: grapevine.example.com/support
- Email: support@grapevine.example.com
- GitHub Issues: github.com/grapevine/issues

### Resources
- User Manual
- Video Tutorials
- FAQ
- Community Forums 