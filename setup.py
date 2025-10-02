from setuptools import setup, find_packages

setup(
    name="marketing-project",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # See requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "marketing-project = marketing_project.main:cli",
        ],
    },
    author="Ibrahim Abouhashish",
    description="A marketing agentic project",
    license="MIT",
)
