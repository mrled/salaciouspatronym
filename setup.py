import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="salaciouspatronym",
    version="3.0.0",
    author="Micah R Ledbetter",
    author_email="me@micahrl.com",
    description="turns out i have a very juvenile sense of humor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrled/salaciouspatronym/",
    packages=["salaciouspatronym"],
    package_data={"salaciouspatronym": ["pantheon.sqlite"]},
    python_requires=">=3.9",
    include_package_data=True,
    install_requires=["tweepy"],
    entry_points={
        "console_scripts": ["salaciouspatronym=salaciouspatronym.cli:main"],
    },
)
