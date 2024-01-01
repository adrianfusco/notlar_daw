from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='notlar',
    version='0.12',
    author='Adrian Fusco',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'notlar = notlar.wsgi:run_gunicorn',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.10',
    ],
    include_package_data=True
)
