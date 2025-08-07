from setuptools import setup, find_packages

setup(
    name="penvstp",
    version="0.1.2",
    description="Environment setup automation script",
    packages=find_packages(),
    install_requires=["pydantic"],
    entry_points={
        'console_scripts': [
            'penvstp=penvstp.cli:main',
        ],
    }
)
