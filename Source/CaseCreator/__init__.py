import os
import glob

# /c:/Users/Ridwa/Desktop/CFD/01_CFD_Software_Development/SplashCaseCreatorCFD/SplashCaseCreatorCFD/src/__init__.py


# Automatically import all Python files in the current directory
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]