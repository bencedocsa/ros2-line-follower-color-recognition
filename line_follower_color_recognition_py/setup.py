from setuptools import find_packages, setup

package_name = 'line_follower_color_recognition_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='docsabence',
    maintainer_email='docsabence903@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'line_follower = line_follower_color_recognition_py.line_follower:main',
            'save_training_images = line_follower_color_recognition_py.save_training_images:main',
        ],
    },
)
