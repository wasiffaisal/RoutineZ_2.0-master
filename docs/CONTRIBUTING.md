# Contributing to RoutineZ

Thank you for your interest in contributing to RoutineZ! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- **Be respectful**: Welcome newcomers and be patient with questions
- **Be collaborative**: Work together to find the best solutions
- **Be constructive**: Provide helpful feedback and suggestions
- **Be inclusive**: Ensure everyone feels welcome to participate

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at wasif.faisal@bracu.ac.bd

## Getting Started

### Prerequisites
- **Python 3.8+** for backend development
- **Node.js 16+** for frontend development
- **Git** for version control
- **VS Code** (recommended) or your preferred IDE

### Setting Up Development Environment

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/RoutineZ_2.0.git
cd RoutineZ_2.0

# Add upstream remote
git remote add upstream https://github.com/cswasif/RoutineZ_2.0.git
```

#### 2. Install Dependencies
```bash
# Backend setup
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../USIS/usis-frontend
npm install
```

#### 3. Environment Setup
```bash
# Copy environment templates
cp .env.example .env.local

# Fill in your API keys and configurations
# Backend: api/.env
# Frontend: USIS/usis-frontend/.env.local
```

## Development Workflow

### Branch Naming Convention
- **Feature branches**: `feature/description`
- **Bug fixes**: `fix/issue-description`
- **Documentation**: `docs/update-description`
- **Refactoring**: `refactor/component-name`

### Workflow Steps

#### 1. Create Feature Branch
```bash
git checkout master
git pull upstream master
git checkout -b feature/your-feature-name
```

#### 2. Make Changes
- Write code following our standards
- Add/update tests
- Update documentation
- Commit frequently with clear messages

#### 3. Test Changes
```bash
# Backend tests
cd api
pytest

# Frontend tests
cd USIS/usis-frontend
npm test
```

#### 4. Push and Create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## Code Standards

### Python (Backend)

#### Style Guide
- **PEP 8**: Follow Python style guide
- **Black**: Use Black for formatting (`black .`)
- **Flake8**: Linting with flake8 (`flake8 .`)
- **Type hints**: Use type annotations where appropriate

#### Example
```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Course:
    """Represents a university course."""
    code: str
    title: str
    credits: int
    schedule: Optional[List[str]] = None

def validate_course(course: Course) -> bool:
    """Validate course data."""
    return bool(course.code and course.title and course.credits > 0)
```

#### Naming Conventions
- **Classes**: PascalCase (`CourseScheduler`)
- **Functions/variables**: snake_case (`calculate_schedule`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_CREDITS`)
- **Private**: _leading_underscore (`_internal_method`)

### JavaScript/React (Frontend)

#### Style Guide
- **ESLint**: Follow ESLint configuration
- **Prettier**: Use Prettier for formatting
- **TypeScript**: Prefer TypeScript for new files
- **React conventions**: Follow React best practices

#### Example
```typescript
import React, { useState, useEffect } from 'react';

interface Course {
  code: string;
  title: string;
  credits: number;
}

interface CourseListProps {
  courses: Course[];
  onSelectCourse: (course: Course) => void;
}

export const CourseList: React.FC<CourseListProps> = ({ 
  courses, 
  onSelectCourse 
}) => {
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  return (
    <div className="course-list">
      {courses.map(course => (
        <CourseCard 
          key={course.code} 
          course={course} 
          onClick={onSelectCourse}
        />
      ))}
    </div>
  );
};
```

### CSS/Styling

#### Tailwind CSS
- **Utility-first**: Use Tailwind utility classes
- **Responsive**: Use responsive prefixes (`sm:`, `md:`, `lg:`)
- **Custom components**: Create reusable components for complex styles

#### Example
```jsx
// Good: Utility classes
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 className="text-lg font-semibold text-gray-900">Course Schedule</h2>
  <button className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700">
    Add Course
  </button>
</div>

// Good: Custom component for reusability
const Card = ({ children, className }) => (
  <div className={`p-4 bg-white rounded-lg shadow ${className}`}>
    {children}
  </div>
);
```

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots of UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process
1. **Automated checks**: CI/CD pipeline runs
2. **Code review**: At least one maintainer reviews
3. **Testing**: Manual testing for significant changes
4. **Approval**: Maintainer approves and merges

## Issue Guidelines

### Bug Reports
Use this template:
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 2.0.0]
```

### Feature Requests
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this be implemented?

**Alternatives**
Other solutions considered

**Additional Context**
Any other relevant information
```

## Testing Guidelines

### Backend Testing

#### Test Structure
```
api/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_ai_service.py
│   └── test_data_loader.py
```

#### Test Categories
- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Mock tests**: Mock external services

#### Example Test
```python
import pytest
from routinez.ai_service import generate_schedule

class TestAIService:
    def test_generate_schedule_valid_courses(self):
        courses = [
            {"code": "CSE101", "credits": 3},
            {"code": "CSE102", "credits": 3}
        ]
        result = generate_schedule(courses)
        assert "schedule" in result
        assert len(result["schedule"]) > 0

    def test_generate_schedule_empty_courses(self):
        result = generate_schedule([])
        assert result["error"] == "No courses provided"
```

### Frontend Testing

#### Test Structure
```
USIS/usis-frontend/
├── src/
│   ├── __tests__/
│   ├── components/__tests__/
│   └── utils/__tests__/
```

#### Test Types
- **Unit tests**: Test individual components
- **Integration tests**: Test component interactions
- **E2E tests**: Test complete user flows

#### Example Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { CourseSelector } from '../CourseSelector';

describe('CourseSelector', () => {
  test('renders course options', () => {
    const courses = [{ code: 'CSE101', title: 'Intro to CS' }];
    render(<CourseSelector courses={courses} />);
    
    expect(screen.getByText('CSE101')).toBeInTheDocument();
  });

  test('handles course selection', () => {
    const mockOnSelect = jest.fn();
    const courses = [{ code: 'CSE101', title: 'Intro to CS' }];
    
    render(
      <CourseSelector 
        courses={courses} 
        onSelectCourse={mockOnSelect} 
      />
    );
    
    fireEvent.click(screen.getByText('CSE101'));
    expect(mockOnSelect).toHaveBeenCalledWith(courses[0]);
  });
});
```

## Documentation

### Code Documentation
- **Docstrings**: Use Google-style docstrings for Python
- **JSDoc**: Use JSDoc for JavaScript functions
- **README updates**: Update README for new features
- **API docs**: Update API.md for endpoint changes

### Documentation Standards
```python
def calculate_schedule_conflicts(schedule1, schedule2):
    """
    Calculate conflicts between two course schedules.
    
    Args:
        schedule1 (dict): First course schedule with 'days' and 'time'
        schedule2 (dict): Second course schedule with 'days' and 'time'
    
    Returns:
        dict: Conflict information including type and severity
        
    Example:
        >>> schedule1 = {'days': ['Mon', 'Wed'], 'time': '10:00-11:30'}
        >>> schedule2 = {'days': ['Mon', 'Fri'], 'time': '10:30-12:00'}
        >>> conflicts = calculate_schedule_conflicts(schedule1, schedule2)
    """
```

## Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

#### 1. Prepare Release
```bash
# Create release branch
git checkout -b release/v2.1.0

# Update version numbers
# Update CHANGELOG.md
# Update documentation
```

#### 2. Test Release
```bash
# Run full test suite
npm test && pytest

# Manual testing
# Performance testing
# Security review
```

#### 3. Create Release
```bash
# Tag release
git tag v2.1.0
git push origin v2.1.0

# Create GitHub release
# Include release notes
# Attach binaries if needed
```

### Hotfix Process
For urgent fixes:

```bash
# Create hotfix branch
git checkout -b hotfix/v2.0.1

# Make minimal changes
# Test thoroughly
# Create PR with "hotfix" label
```

## Development Tools

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "eamodio.gitlens",
    "ms-vscode.vscode-json"
  ]
}
```

### Git Hooks
We use pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Development Scripts
```bash
# Backend development
npm run dev:backend    # Start backend in development mode
npm run test:backend # Run backend tests
npm run lint:backend # Lint backend code

# Frontend development  
npm run dev:frontend  # Start frontend in development mode
npm run test:frontend # Run frontend tests
npm run lint:frontend # Lint frontend code

# Full development
npm run dev          # Start both frontend and backend
npm run test         # Run all tests
npm run lint         # Lint all code
```

## Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time discussion [Join here](https://discord.gg/routinez)
- **Email**: wasif.faisal@bracu.ac.bd

### Resources
- **Documentation**: [docs/README.md](./README.md)
- **API Reference**: [docs/API.md](./API.md)
- **Setup Guide**: [docs/SETUP.md](./SETUP.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](./DEPLOYMENT.md)

### First-time Contributors
Welcome! Here's how to get started:

1. **Look for "good first issue" labels**
2. **Read the documentation thoroughly**
3. **Ask questions in Discord**
4. **Start with small contributions**
5. **Follow the review process**

### Recognition
Contributors are recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Special mentions** in project updates

Thank you for contributing to RoutineZ! Your efforts help make university scheduling easier for students worldwide.