from setuptools import find_packages, setup

package_name = 'warehouse_robot_llm'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='Anton Ilin',
    maintainer_email='antonilin17@users.noreply.github.com',
    description='Keyword baseline and optional Mistral interface for warehouse navigation',
    license='NOASSERTION',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'keyword_nav_node = warehouse_robot_llm.llm_nav_node:main',
            'llm_nav_node = warehouse_robot_llm.llm_nav_node:main',
            'mistral_nav_node = warehouse_robot_llm.mistral_nav_node:main',
        ],
    },
)
