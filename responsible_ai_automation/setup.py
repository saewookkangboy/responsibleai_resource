"""Setup script for Responsible AI Automation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="responsible-ai-automation",
    version="0.1.0",
    author="Responsible AI Automation Contributors",
    author_email="your-email@example.com",
    description="AI 윤리와 Responsible AI 원칙을 자동으로 학습, 최적화, 적용하는 강화 학습 기반 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/responsible-ai-automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/responsible-ai-automation/issues",
        "Source": "https://github.com/yourusername/responsible-ai-automation",
        "Documentation": "https://github.com/yourusername/responsible-ai-automation#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "responsible-ai=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

