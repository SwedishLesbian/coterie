# Contributing to Coterie

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- SQLite 3
- PyQt6

### Development Environment Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/coterie.git
cd coterie
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize database
```bash
python -m coterie.db.init
```

## Development Process

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

### Commit Guidelines
- Use descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Reference issue numbers when applicable
- Keep commits focused and atomic

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document classes and functions
- Keep functions focused and under 50 lines
- Use meaningful variable names

### Testing
- Write unit tests for new features
- Update existing tests when modifying code
- Ensure all tests pass before submitting PR
- Maintain test coverage above 80%

## Pull Request Process

1. Create feature/bugfix branch
2. Implement changes with tests
3. Update documentation
4. Run linting and tests
5. Submit pull request
6. Address review comments
7. Merge after approval

## Issue Reporting

### Bug Reports
Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- System information
- Screenshots if applicable

### Feature Requests
Include:
- Clear description
- Use case
- Expected behavior
- Proposed implementation

## Code Review

### Review Checklist
- Code follows style guide
- Tests are included
- Documentation is updated
- No unnecessary dependencies
- Performance considerations
- Security implications

### Review Process
1. Submit PR
2. Automated checks run
3. Code review by maintainers
4. Address feedback
5. Final approval
6. Merge

## Documentation

### Required Documentation
- Code comments
- Function/class docstrings
- README updates
- API documentation
- User guide updates

### Documentation Style
- Clear and concise
- Examples where helpful
- Proper formatting
- Keep up to date

## Release Process

### Version Numbering
- Major.Minor.Patch
- Follow semantic versioning
- Document breaking changes

### Release Steps
1. Update version number
2. Update changelog
3. Create release branch
4. Run full test suite
5. Build distribution
6. Create release tag
7. Merge to main

## Community

### Communication
- GitHub Issues
- Pull Requests
- Project Wiki
- Developer Chat

### Code of Conduct
- Be respectful
- Welcome newcomers
- Focus on improvement
- Constructive feedback

## Support

### Getting Help
- Check documentation
- Search existing issues
- Ask in discussions
- Submit detailed questions

### Resources
- Project Wiki
- API Documentation
- User Guide
- FAQ 