
from setuptools import setup, find_packages

def read_readme():
    with open('README.md') as f:
        return f.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'gspread',
]

setup(
    name='clerk',
    version='0.1.0',
    description='A clerk bot for tracking logs',
    long_description= read_readme(),
    long_description_content_type="text/markdown",
    author='Lucas Liu',
    author_email='llychinalz@gmail.com',
    url='https://github.com/LiyuanLucasLiu/clerk',
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
    install_requires=requirements,
    license='Apache License 2.0',
    entry_points={
        'console_scripts': ['clerk=clerk.commands:run'],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ]
)