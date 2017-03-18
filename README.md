# LandscapeSim
LandscapeSim provides a RESTful web API for State and Transition Simulation Models (STSMs) stored in a
[SyncroSim](syncrosim.com) data store. LandscapeSim also provides a configurable interface for running existing STSMs,
allowing users to manipulate model parameters to experiment and compare different scenario outcomes.

# Why?
We needed to provide a reusable, extensible interface that transports information easily to incorporate STSM models into
 web-based tools for landscape managers and researchers. This allows us to drive visualization tools for the web, while utilizing a standardized platform.

# Use cases
[landscapesim.org](http://landscapesim.org) utilizes a simplified version of LandscapeSim, enabling users of the model to run STSMs from within a web application.
It provides a simple toolbox using SyncroSim's ST-Sim model process and exposes the model run results to drive the visualizations, including 3D terrain visualization, charts and tables.

# Attribution
LandscapeSim would not be possible without the work on [SyncroSim](syncrosim.com) from Colin J. Daniel, Leonardo Fid, Benjamin M. Sleeter, 
Marie-Josee Fortin, and many, many others pushing the bounds on spatially explicit simulation models focused on ecology and landscape management.

Daniel, C., Frid, L., Sleeter, B., & Fortin, M. J. 2016. [State-and-transition simulation models: a framework for 
forecasting landscape change.](http://dx.doi.org/10.1111/2041-210X.12597) Methods in Ecology and Evolution. doi:10.1111/2041-210X.12597

# Developer Documentation
TODO