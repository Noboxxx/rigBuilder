import os

from maya import cmds
from rigBuilder.files.core import JsonFile
from rigBuilder.steps.core import StepBuilder


def batch(files):
    cmds.loadPlugin('matrixNodes')
    cmds.loadPlugin('quatNodes')

    for f in files:
        stepBuilder = JsonFile(f).load()

        if not isinstance(stepBuilder, StepBuilder):
            print('file \'{}\' ain\'t stepBuilder.'.format(f))
            continue

        # build
        stepBuilder.build()

        # Save build
        dirname, basename = os.path.split(f)
        outputFile = os.path.join(dirname, 'build.ma')
        cmds.file(rename=outputFile)
        cmds.file(save=True, type="mayaAscii")


"""
import sys
sys.path.append(r'O:\TRICO\10_Recherche\pierre\lib')

from maya import standalone
standalone.initialize()

from rigBuilder.batch import batch
files = (
    r'O:\TRICO\10_Recherche\pierre\lib\HumanBodyRig\stepBuilder.json',
    r'O:\TRICO\10_Recherche\pierre\lib\raptorRig\stepBuilder.json',
)
batch(files)

"""