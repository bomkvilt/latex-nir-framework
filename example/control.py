# since the project is an example it's an only way to include the framework
from os import path
import sys

sys.path.append("..")
from framework import Framework

# connext the framework to a command line
framework = Framework()
framework.processArgs()
