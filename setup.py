import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-bitbay",
    version="0.1.1",
    author="Cai Yundong",
    author_email="yundong.cai@gmail.com",
    description="Bitbay Exchange API python implementation for automated trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caiyundong/bitbay_api_python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
