# Contributing to Korean Forced Aligner

Thank you for your interest in contributing to the Korean Forced Aligner project!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- The use case or problem it solves
- Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. Push to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a pull request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small
- Write docstrings for functions and classes

### Testing

- Test your changes before submitting
- Run the basic test suite: `python test_basic.py`
- Add tests for new features when possible

### Development Setup

1. Clone your fork
   ```bash
   git clone https://github.com/YOUR-USERNAME/kfaligner.git
   cd kfaligner
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Make your changes and test
   ```bash
   python app.py
   ```

## Areas for Contribution

We especially welcome contributions in these areas:

- **Alignment Accuracy**: Integrate better forced alignment algorithms (MFA, Kaldi)
- **Korean Language Support**: Improve Korean text processing and tokenization
- **UI/UX**: Enhance the web interface with visualizations
- **Performance**: Optimize processing speed
- **Documentation**: Improve docs, add tutorials, create examples
- **Testing**: Add comprehensive test coverage
- **Deployment**: Kubernetes configs, CI/CD pipelines

## Questions?

Feel free to open an issue for any questions or reach out to the maintainers.

Thank you for contributing!
