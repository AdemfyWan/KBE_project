DIRECTORY STRUCTURE:
─ Assignment
  ├── AssignmentMain [ROOT]
  │   ├── Airfoils
  │   ├── Output
  │   └── <py files> 
  └── Q3D
      └── <matlab files>


ADDITIONAL INSTALLATIONS NEEDED:
- MATLAB R2021b (later versions not compatible with Python 3.7)
- MATLAB engine API for python
- Python libraries: (go to terminal -> type "pip install <libraryname>", e.g. "pip install pandas")
	- pandas (to read excel file)
	- numpy
	- fpdf
	- openpyxl
	- matplotlib


INPUT FILES:
- input.xlsx -> Only change "Value" column
	- Min, max, & default values shown are for information purposes only, will not change coded limits
	- Warning messages will appear if inputs are beyond limits. Values will automatically be set within limits.
- Airfoil files -> .dat files must be placed in "Airfoils" folder
	- Must be placed in "Airfoils" folder
	- Must be a Selig format .dat file (LE -> upper surface -> 0,0 -> lower surface -> TE)
	- Must have closed TE


OUTPUT FILES:
- STEP file -> Right click "step_writer" part -> click "write"
- Design report PDF -> Evaluate "output_pdf" attribute. Includes 2 figures which can be evaluated independently:
	- CG Analysis: Evaluate "cg_analysis" attribute
	- Planform: Evaluate "planform_plot" attribute
- All output files will be saved in "Output" folder
