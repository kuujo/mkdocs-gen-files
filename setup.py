from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="mkdocs-import-plugin",
    version="0.1.0",
    author="Jordan Halterman",
    author_email="jordan.halterman@gmail.com",
    description="MkDocs plugin for importing Markdown files from URLs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    license="MIT",
    packages=find_packages(
        exclude=["tests"]
        ),
    install_requires=[
        "mkdocs>=1.0.4",
        "asyncio",
        "tqdm"
        ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "mkdocs.plugins": [
            "import = mkdocs_import_plugin.plugin:ImportPlugin"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"
    ],
)

