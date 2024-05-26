from setuptools import setup, find_packages

setup(
    name='aristech',
    version='0.1.0',
    description='Aristech - Outil de défense des apiculteurs contre le frelon asiatique',
    author='Aristech',
    author_email='contact@aristech.org',
    url='https://github.com/votre-utilisateur/aristech',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'librosa',
        'pyaudio',
        'tensorflow',
        'torch',
        'torchvision',
        'opencv-python',
        'opencv-python-headless',
        'pyyaml',
        'flask',
        'flask-restful',
        'scipy',
        'RPi.GPIO',
        'jupyter',
        'paho-mqtt',
        'lora',
        'pigpio',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'aristech=src.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
)