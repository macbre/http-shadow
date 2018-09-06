from setuptools import setup

setup(
    name='shadow',
    version='0.0.1',
    description='',
    url='https://github.com/macbre/http-shadow',
    author='macbre',
    author_email='macbre@wikia-inc.com',
    install_requires=[
        'requests==2.19.1',
        'wikia-common-kibana==2.2.5',
    ],
    include_package_data=True,
)
