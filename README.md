# LandscapeSim
![site_icon](https://github.com/consbio/landscapesim/blob/master/landscapesim/static/img/site_icon.png)

LandscapeSim provides a RESTful web API for running State and Transition Simulation Models (STSMs) and collecting tabular
and spatially referenced data stored in [SyncroSim](syncrosim.com) data stores. LandscapeSim also provides a configurable interface
for modifying parameters for existing STSMs, allowing users to experiment and compare different scenario outcomes from customized,
web-based applications.

# Developer Documentation
See the [wiki](https://github.com/consbio/landscapesim/wiki) within this repo!

# Why?
We needed to provide a reusable and extendable interface that transports information easily to incorporate STSM models into
 web-based tools for landscape managers and researchers. This allows us to drive visualization tools for the web while utilizing
 a standardized platform that can be incorporated into other tools.

# Use cases
[landscapesim.org](http://landscapesim.org) utilizes a custom implementation of LandscapeSim, enabling managers and researchs to utilize 
 information provided from STSMs from within a web application. It provides a simple toolbox to change parameters to an STSM model and
 exposes results to drive the visualizations in the tool, including 3D terrain visualizations, tables and charts.

# Attribution
Project funding was provided by the Bureau of Land Management through Oregon State University (AwardL14AC00103).
A special thanks to  Dr. Louisa Evers (BLM) for her continued support.

LandscapeSim would not be possible without the exhaustive work on [SyncroSim](http://syncrosim.com) from Colin J. Daniel, Leonardo Frid, Benjamin M. Sleeter, 
Marie-Josee Fortin, and many, many others pushing the bounds on spatially explicit simulation models focused on ecology and landscape management.

Daniel, C., Frid, L., Sleeter, B., & Fortin, M. J. 2016. [State-and-transition simulation models: a framework for 
forecasting landscape change.](http://dx.doi.org/10.1111/2041-210X.12597) Methods in Ecology and Evolution. doi:10.1111/2041-210X.12597
