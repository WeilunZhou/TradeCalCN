from setuptools import setup

setup(
    name='TradeCalCN',
    version='0.1',
    description='A small Python module for trading days in China stock market',
    author='WeilunZhou',
    author_email='3227740026@qq.com',
    packages=['TradeCalCN'],
    install_requires=['baostock>=0.8.8'],
    python_requires='>=3.7'
)
