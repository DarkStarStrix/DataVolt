from setuptools import setup, find_packages

setup(
    name='datastream',
    version='0.0.1',
    author='Allan',
    author_email='allaw.mk@gmail.com',
    description='A modular toolkit for data engineering pipelines',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/dataflux',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.9+',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=[
        'pandas>=1.3.0',
        "numpy==1.22.0",
        "scikit-learn==1.5.0",
        'neptune-client>=0.9.0',
        "torch==2.5.0",
        'setuptools~=70.0.0',
        'pillow~=11.0.0',
        'joblib~=1.4.2',
        'boto3~=1.35.88',
        'sqlalchemy~=1.4.0'
    ],
)
