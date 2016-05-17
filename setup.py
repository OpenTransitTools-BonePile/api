from setuptools import find_packages, setup

setup(
    name='ott.api',
    version='0.1.0',
    author='Grant Humphries',
    dependency_links=[
        'git+https://github.com/OpenTransitTools/'
        'otp_client_py.git#egg=ott.otp_client',
    ],
    description='Wrapper for the OpenTripPlanner API that includes '
                'geocoding functionality',
    entry_points={
        'console_scripts': [
            'trip_planner = ott.otp_client.trip_planner:main',
            'app = ott.api.app:main'
        ]
    },
    install_requires=[
        'flask>=0.10.1',
        'ott.otp_client>=0.1.0',
        'webargs>=1.3.2'
    ],
    license='Mozilla 2.0',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    url='https://github.com/OpenTransitTools/api'
)
