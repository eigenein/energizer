import setuptools

setuptools.setup(
    name='energizer',
    version='0.1',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    description='Enelogic + Buienradar + Telegram = ❤️',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eigenein/energizer',
    packages=setuptools.find_packages(exclude=['tests']),
    python_requires='>=3.7',
    install_requires=[
        'aiohttp',
    ],
    extras_require={},
    entry_points={
        'console_scripts': ['energizer = energizer:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Home Automation',
    ],
    zip_safe=True,
)
