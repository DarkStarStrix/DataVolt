import os
from setuptools import setup, find_packages

# Check if README.md exists
readme = "README.md"
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
print(f"Files in the directory: {os.listdir(current_dir)}")

readme_path = os.path.join(current_dir, readme)
print(f"Full path to README.md: {readme_path}")

if os.path.exists(readme_path):
    with open(readme_path, "r") as fh:
        long_description = fh.read()
    print("README.md found and read successfully.")
    print("Contents of README.md:")
    print(long_description)
else:
    long_description = "A reusable workflow for data engineering pipelines"
    print("README.md not found. Using default long description.")

setup(
    name="DataVolt",
    version="0.0.1",
    author="Allan",
    author_email="allanw.mk@gmail.com",
    description="A reusable workflow for data engineering pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DarkStarStrix/DataVolt",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9,<3.12',
)
