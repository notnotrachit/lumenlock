# Contributing to LumenLock

Thank you for your interest in contributing to LumenLock! We welcome contributions from the community to help make this project better. whether it's fixing bugs, adding new features, or improving documentation.

## Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Fork the repository**
   Click the "Fork" button at the top right of the repository page to create your own copy.

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/lumenlock.git
   cd lumenlock
   ```

3. **Set up a virtual environment**
   It is recommended to use a virtual environment to manage dependencies.
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   The app will be available at `http://127.0.0.1:8000/`.

## Development Workflow

1. **Create a new branch**
   Always work on a new branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-bug-name
   ```

2. **Make your changes**
   Write clear, maintainable code. If you are adding a new feature, try to include comments where necessary.

3. **Test your changes**
   Ensure that the application runs correctly and that your changes don't break existing functionality.
   (We are working on adding a test suite - contributions there are welcome!)

## Submitting a Pull Request

1. **Commit your changes**
   Write a clear, descriptive commit message.
   ```bash
   git commit -m "Add feature X"
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request**
   Go to the original repository and click "New Pull Request".
   - Select your branch.
   - Provide a clear title and description of your changes.
   - Link to any relevant issues (e.g., "Fixes #1").

## Code Style

- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.
- **HTML/CSS**: Keep templates clean and organized.

## Reporting Bugs

If you find a bug, please open an issue on GitHub with the following details:
- Description of the bug.
- Steps to reproduce.
- Expected vs. actual behavior.
- Screenshots (if applicable).

## Need Help?

If you have any questions, feel free to open an issue or ask in the discussions.

Happy Coding! 🚀
