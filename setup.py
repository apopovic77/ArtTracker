from setuptools import setup, find_packages

setup(
    name='ArtTracker',
    version='0.1.0',
    author='Alexander Popovic',
    author_email='apopovic.aut@gmail.com',
    description='Efficient person tracking using YOLOv8 and ZeroMQ (Zmq)',
    long_description='ArtTracker is an efficient and easy-to-use software application designed to track and identify people using the YOLOv8 algorithm. It utilizes ZeroMQ (Zmq) for seamless communication between publishers and subscribers, ensuring reliable transmission of tracked person data.',
    long_description_content_type='text/markdown',
    url='https://github.com/apopovic77/ArtTracker',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'numpy',
        'opencv-python',
        'pyzmq',
        'ultralytics',
        'supervision',
        'pafy',
        'lapx',
    ],
    python_requires='>=3.10',
)