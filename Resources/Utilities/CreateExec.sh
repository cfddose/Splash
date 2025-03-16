#!/bin/sh
#========

rm -rf Splash build dist Splash.spec 

pyinstaller --noconfirm --onefile \
--add-data "Resources:Resources" \
--add-data "Meshing:Meshing" \
--add-data "CaseCreator:CaseCreator" \  # Add the CaseCreator directory
--name Splash Source/Splash.py

cp dist/Splash Source/
