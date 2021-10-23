
def main():

    from setuptools import setup, find_packages

    console_scripts = ["e3smdiff=e3smdiff.main:main"]
    install_requires = []

    setup(
        name="e3smdiff",
        version="0.1.0",
        description="E3SM DIFF",
        long_description="E3SM DIFF",
        author="Youngsung Kim",
        author_email="youngsung.kim.act2@gmail.com",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
        keywords="e3sm",
        packages=find_packages(exclude=["tests"]),
        include_package_data=True,
        install_requires=install_requires,
        entry_points={ "console_scripts": console_scripts},
        project_urls={
            "Bug Reports": "https://github.com/grnydawn/e3smdiff/issues",
            "Source": "https://github.com/grnydawn/e3smdiff",
        }
    )

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
