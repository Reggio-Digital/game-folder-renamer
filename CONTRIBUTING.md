# Contributing to Game Folder Renamer

Thank you for your interest in contributing to Game Folder Renamer! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Any examples or mockups if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes thoroughly
3. **Update documentation** if needed (README.md)
4. **Commit your changes** with clear, descriptive commit messages
5. **Push to your fork** and submit a pull request

#### Code Style Guidelines

- Use meaningful variable and function names
- Follow PEP 8 style guidelines for Python code
- Keep functions focused and single-purpose
- Add docstrings to functions and classes

#### Testing Your Changes

Before submitting a pull request:
1. Test the app with `streamlit run app.py`
2. Verify all features work as expected
3. Test with different folder structures
4. Check that error handling works properly

### Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/game-folder-renamer.git
   cd game-folder-renamer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. Make your changes and test locally

6. Commit and push:
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
