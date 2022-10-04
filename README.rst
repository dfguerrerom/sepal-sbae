.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT


SEPAL Sample Based Area Estimator
---------------------------------

.. image:: https://raw.githubusercontent.com/sepal-contrib/sepal-sbae/master/doc/img/intro.PNG
   :align: center

Sampling desing
===============

1. random / systematic: the script will calculate the grid based on the given grid_size and then it will create a point in the center (systematic) or it will randomly select a point within each of the cells. 

Depending on the input design (random/systematic) and on the grid size, this calculation can be done directly on-the-fly and export the results directly to the SEPAL enviroment. 

.. note::
    if you experience "out of memory" errors, it means that the computation couldn't be completed on-the-fly. In that case, the computation can be triggered as Google Earth Engine task as GEE Asset or sent to Google Drive.
    
.. image:: https://raw.githubusercontent.com/systematic_sample.PNG
   :align: center



SABE from categorical image
===========================

The objective of the SBAE analysis is to simulate the area of the given class from a categorical image using the proportion of points (samples) that falls into that category compared with the overall area. This estimation can be then compared with the real class area and get the simulated error by class. 

This simulation is then repeated several times varying the cell size and capturing the error for each category and an overall value (representing the mean), then a plot is generated as a function of the grid density and the simulated area and so we can determine the inflexion point or look at what error level determine the size of the grid that captures the change with a given level of acceptable error.

To perform the sample area based estimation from a categorical image, select the type of design and the grid shape within the :code:`design` tab. Then click on the SBAE tab and select your categorical asset.


.. image:: https://raw.githubusercontent.com/sepal-contrib/sepal-sbae/master/doc/img/sbae_graph_sample
   :align: center
