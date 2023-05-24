FOLDER DIRECTORY:

-- Assignment
 |-- AssignmentMain
 | |-- Airfoils
 | |-- Output
 | |-- <py files>
 |-- Q3D
   |-- <matlab files>


ADDITIONAL INSTALLATIONS NEEDED:

- MATLAB R2021b (later versions not compatible with Python 3.7)
- MATLAB engine API for python (KBE tutorial 11)
- Python libraries: (go to terminal -> type "pip install <libraryname>", e.g. "pip install pandas")
	- pandas (to read excel file)
	- numpy
	- fpdf
	- openpyxl
	- matplotlib


INPUT FILES:

- input.xlsx -> Only change "Value" column
- Airfoil files -> .dat files must be placed in "Airfoils" folder


OUTPUT FILES:

- STEP file -> Right click "step_writer" part -> click "write"
- Design report PDF -> Evaluate "output_pdf" attribute
- All output files will be saved in "Output" folder
