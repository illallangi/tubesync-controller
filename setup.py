import setuptools

# Define version
__version__ = "development"
exec(open("tubesync-controller/__version__.py").read())
print(__version__)

# Define readme
with open("README.md", "r") as fh:
    long_description = fh.read()

# Define requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="tubesync-controller",
    version=__version__,
    author="Andrew Cole",
    author_email="andrew.cole@illallangi.com",
    description="TubeSync Controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/illallangi/tubesync-controller",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={},
    install_requires=requirements,
)
