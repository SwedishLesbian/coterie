# Coterie Issue Tracking

## High Priority Issues

### UI-001: Character Creation Validation
- **Status**: Open
- **Description**: Character creation dialog lacks input validation, allowing invalid data
- **Impact**: Data integrity issues, potential database corruption
- **Target**: Next sprint

### UI-002: Trait Widget Dot Alignment
- **Status**: Open
- **Description**: Dots in trait widget not properly aligned with spin box
- **Impact**: Poor visual presentation and user experience
- **Target**: Current sprint

### DB-001: Database Error Handling
- **Status**: Open
- **Description**: Missing error handling for database operations
- **Impact**: Silent failures, potential data loss
- **Target**: Next sprint

## Medium Priority Issues

### UI-003: Window Resize Issues
- **Status**: Open
- **Description**: Main window does not resize properly
- **Impact**: Poor user experience on different screen sizes
- **Target**: Future sprint

### DB-002: Connection Pooling
- **Status**: Open
- **Description**: Need to implement connection pooling
- **Impact**: Potential performance bottleneck
- **Target**: Future sprint

## Resolved Issues

### UI-000: Initial Window Size
- **Status**: Resolved
- **Description**: Main window opened with incorrect default size
- **Resolution**: Set proper default size in MainWindow constructor
- **Fixed In**: Initial commit

### DB-000: SQLite Path Configuration
- **Status**: Resolved
- **Description**: Database path not properly configured for different OS
- **Resolution**: Implemented proper path handling using pathlib
- **Fixed In**: Initial commit

## Issue Management

### Categories
- UI/Main Window
- UI/Character Sheet
- UI/Dialogs
- UI/Widgets
- Data Layer
- Business Logic

### Priority Levels
- **High**: Critical functionality, data integrity
- **Medium**: Important features, significant UX
- **Low**: Nice-to-have, cosmetic issues

### Resolution Process
1. Issue identified and logged
2. Priority assigned
3. Developer assigned
4. Fix implemented
5. Testing completed
6. Issue closed 