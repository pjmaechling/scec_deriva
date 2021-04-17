# SCEC Forecast Data Management using Deriva
This is a collection of software developed to support SCEC's forecast data management activity. SCEC produces both short-term earthquake forecasts and earthquake forecast evaluation methods. SCEC is developing a forecast data management approach based on the Deriva software system. The initial prototype is designed to manage ETAS forecasts and evaluations.

## Description of Scripts in Repo
* scec_config.py
This scripts adds annotations to the ERD
* scec_model.py
This script creates a minimal ERD used to define the ETAS forecast and evaluations.

* create_erd.py
This script creates the SCEC ETAS forecast and evaluation schema using the Deriva Chisel library. We iterated through several version of the initial ERD format. The most recent version of this script includes ERD creation and specification of Deriva annotations. These scripts point at the SCEC catalog in a Deriva sandbox.

## Project Description
See project wiki.

## Contributors
Philip Maechling

Rob Schuler

Carl Kesselman

