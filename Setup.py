from setuptools import setup, find_packages

setup(
    name="ai-urinalysis-pro",
    version="3.0.0",
    author="Dr. Precious Belema Ibiabuo",
    description="Comprehensive AI-powered urinalysis system",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "kivy>=2.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
    ],
    extras_require={
        "ai": ["inference-sdk>=0.9.0"],
        "pdf": ["reportlab>=4.0.0"],
        "qr": ["qrcode[pil]>=7.4.0"],
    },
)
