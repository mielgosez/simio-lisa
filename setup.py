import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simio_lisa",
    version="0.2.0",
    author="Jose Mielgo",
    author_email="mielgosez@gmail.com",
    description="Beautiful Simio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mielgosez/simio_lisa",
    project_urls={
        "Bug Tracker": "https://github.com/mielgosez/simio_lisa/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["pandas",
                      "numpy"]
)
