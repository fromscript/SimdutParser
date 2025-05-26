from setuptools import setup, find_packages

setup(
    name="simdutparser",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "PyMuPDF>=1.25.5",
        "pyyaml>=6.0"
    ],
    entry_points={
        'console_scripts': [
            'pdf-text-parser=simdutparser.parsers.text_parser:main'
        ]
    },
    include_package_data=True,
    package_data={
        'simdutparser': ['../config/*.yaml']
    },
    python_requires=">=3.8",
)