# 20210513_arcgis-earth-api
Contains several scripts using ArcGIS Earth API to conduct interesting things.
## Files and Description
The project here mainly performs three functions, I will introduce the required files based on functions.
### Calculate Antipodes
- Calculate the antipode of current location, then take 15 pics from high altitude to low.
- **Files**: Antiodes.py
### Region Scanning
- Scan a region stored in kml file. The kml file can be generated by ArcGIS Earth.
- **Files**: WorldScan.py, Proj_60FPS.py, readkml.py, region(folder)
### Tour around the World
- Randomly takes pics in assigned region. Region is stored in kml file.
- **files**: WorldTour.py, readkml.py, region(folder)
### Supported Version
Verified: ArcGIS Earth V1.13
## Author's Comment
- 这个项目做之前其实并不知道大概要做出什么样的东西出来，功能基本上都是天马行空边做边想的，所以组织逻辑很乱。最主要的，还是想做一些有意思的事情。
- *What's life without whimsy?
不为无益之事，何以遣有涯之生。*
