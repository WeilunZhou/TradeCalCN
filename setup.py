from setuptools import setup
from setuptools import find_packages

setup(
    name='TradeCalCN',
    version='0.1',
    description='A small Python module for trading days in China stock market',
    url = 'https://github.com/WeilunZhou/TradeCalCN',
    author='WeilunZhou',
    author_email='3227740026@qq.com',
    packages=find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['baostock>=0.8.8'],
    python_requires='>=3.7'
)
