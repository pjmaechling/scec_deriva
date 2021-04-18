# SCEC Forecast Data Management using Deriva
This is a collection of software developed to support SCEC's forecast data management activity. SCEC produces both short-term earthquake forecasts and earthquake forecast evaluation methods. SCEC is developing a forecast data management approach based on the Deriva software system. The initial prototype is designed to manage ETAS forecasts and evaluations.

## Description of Scripts in Repo
* populate_columns.py
This script queries the forecast table, retrieves all the rows. For each row, it reads the forecast name column, which is a directory name that encodes several metadata fields. It parses that directory name string to extract specific metadata values. It then populates other columns in the row with metadata values extracted.

* add_columns.py
This script parses the ETAS directory names, extracts metadata fields, then adds columns into the ERD to store the extracted metadata fields.

* scec_config.py
This scripts adds annotations to the ERD

* scec_model.py
This script creates a minimal ERD used to define the ETAS forecast and evaluations.

* create_erd.py
This script creates the SCEC ETAS forecast and evaluation schema using the Deriva Chisel library. We iterated through several version of the initial ERD format. The most recent version of this script includes ERD creation and specification of Deriva annotations. These scripts point at the SCEC catalog in a Deriva sandbox.
