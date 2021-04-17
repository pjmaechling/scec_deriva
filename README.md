# scec_deriva
This is a collection of software developed to support SCEC's forecast data management activity. SCEC produces both short-term earthquake forecasts and earthquake forecast evaluation methods. SCEC is developing a forecast data management approach based on the Deriva software system.

## scec_model.py

## scec_config.py
 
## Scripts for implementing Deriva Entity Relationship Diagram (ERD)
## erd_eg_1.py
## erd_eg_2.py
## erd_eg_3.py
We iterate through several version of the initial ERD format.These scripts provides examples showing several versions of how the schema is defined using Deriva Chisel library.

## Lesson's Learned
## Organization of Forecast files
## Existing data management solutions
## 

## Project Description - Earthquake Forecast Data Management Prototype Development
SCEC researchers develop physics-based earthquake models, use these models to make short term earthquake forecasts, and evaluate these forecasts in rigorous ways that determine their usefulness and guide model improvements. 

Forecasts with the potential for significant societal impact must be developed and released using rigorous standards of data management and computational reproducibility. The number and type of digital files associated with forecast models has increased greatly as models advanced. Modern data management cyberinfrastructure (CI) is needed to provide better traceability of data used in models and of results produced by forecasts. Also, we need to demonstrate computational reproducibility for our most significant public forecasts. We must address both the file management and the computational reproducibility challenges together to ensure the original data files and original software source code are available to support forecast reproducibility.

We have initiated a collaborative technical activity between short term earthquake forecast researchers (Jordan, Milner, Savran) and computer scientists (Kesselman, Stodden, Maechling) to improve the usability of modern operational earthquake forecasts by improving the forecast data management and computational reproducibility capabilities. The geoscientists involved are key developers of a USGS operational earthquake forecasting model and of SCEC’s Collaboratory for the Study of Earthquake Predictability (CSEP). The computer scientists involved bring expertise in scientific data management and computational reproducibility.

We are examining a series of short-term earthquake forecasts [Milner et al 2020] and earthquake forecast evaluations [Savran et al 2020] related to the Ridgecrest M7.1 earthquake. In this initial technical evaluation, we are examining the data management and reproducibility of these two forecast research publications. We will register the files and software used to create these forecasts into a Deriva data management system. We will then evaluate the completeness and complexity of the data used in these earthquake forecasts and evaluate the reproducibility of these forecasts.

We believe this activity can inform, and potentially benefit, several earthquake forecasting-related activities and benefit SCEC’s data management and computational reproducibility research. This work will ensure the results from these Ridgecrest ETAS forecast and evaluation publications are complete and reproducible. This work can benefit researchers running similar ETAS studies after significant future California earthquakes. These two papers provide good data management examples for SCEC because they involve both earthquake forecasting and earthquake forecast evaluations. This work may be used to manage future CSEP forecast evaluation results. This work may be useful to earthquake forecast activities such as UCERF developments which will require careful management of many digital files by a large research group.

## References:
Milner, K. R., Field, E. H., Savran, W. H., Page, M. T., & Jordan, T. H. (2020). Operational Earthquake Forecasting during the 2019 Ridgecrest, California, Earthquake Sequence with the UCERF3‐ETAS Model. Seismological Research Letters, 91(3), 1567-1578. doi: https://doi.org/10.1785/0220190294

Savran, W. H., Werner, M. J., Marzocchi, W., Rhoades, D. A., Jackson, D. D., Milner, K. R., Field, E. H., & Michael, A. J. (2020). Pseudo-prospective evaluation of UCERF3-ETAS forecasts during the 2019 Ridgecrest Sequence, Bulletin of the Seismological Society of America, 110(4), 1799-1817. doi: https://doi.org/10.1785/0120200026

## Contributors
Philip Maechling
Rob Schuler
Carl Kesselman
Kevin Milner
William Savran
