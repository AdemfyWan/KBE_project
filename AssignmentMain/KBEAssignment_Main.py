
from math import tan, radians, pi, sqrt
from parapy.core import *
from parapy.core.validate import Range
from parapy.geom import *
from ref_frame import Frame
from liftingsurface import LiftingSurface
from typing import Dict
from parapy.exchange import STEPWriter
from fpdf import FPDF
from datetime import datetime
from AssignmentMain import MATLAB_Q3D_ENGINE
import matlab.engine
import pandas as pd
import numpy
import time
import os

DIR = os.path.dirname(__file__)


def generate_warning(warning_header, msg):
    from tkinter import Tk, messagebox
    window = Tk()  # initialization
    window.withdraw()
    messagebox.showwarning(warning_header, msg)  # generates message box
    window.deiconify()  # kills the gui
    window.destroy()
    window.quit()


# CONSTANTS =======================================================================

GR = 9.80665  # standard gravity
KA = 1.4  # specific heat ratio, air
R = 287  # gas constant (J/kg K)
A = -0.0065  # ISA temperature lapse rate up to alt=11km
T_REF = 288  # reference temperature (K)
M1 = 0.01849557883  # MTOW vs payload ratio function, slope
C1 = 3.769488083  # y-intercept

# READ & VALIDATE INPUT FILE =======================================================

df = pd.read_excel('input.xlsx')

max_payload = 4   # PAYLOAD
min_payload = 0.1
default_payload = 0.5
in_payload = df.iloc[0]['Value']
if numpy.isnan(in_payload):
    print("Payload unspecified")
    in_payload = default_payload
elif in_payload > max_payload:
    msg = "Payload cannot be more than " + str(max_payload) + " kg. "\
          "Payload will be set to " + str(max_payload) + " kg."
    generate_warning("Warning: Payload exceeds maximum", msg)
    in_payload = max_payload
elif in_payload < min_payload:
    msg = "Payload cannot be less than " + str(min_payload) + " kg. " \
          "Payload will be set to " + str(min_payload) + " kg."
    generate_warning("Warning: Payload is less than minimum", msg)
    in_payload = min_payload

max_endurance = 120  # ENDURANCE
min_endurance = 5
default_endurance = 60
in_endurance = df.iloc[1]['Value']
if numpy.isnan(in_endurance):
    print("Endurance unspecified")
    in_endurance = default_endurance
elif in_endurance > max_endurance:
    msg = "Endurance cannot be more than " + str(max_endurance) + " minutes. "\
          "Endurance will be set to " + str(max_endurance) + " minutes."
    generate_warning("Warning: Endurance exceeds maximum", msg)
    in_endurance = max_endurance
elif in_endurance < min_endurance:
    msg = "Payload cannot be less than " + str(min_endurance) + " minutes. " \
          "Payload will be set to " + str(min_endurance) + " minutes."
    generate_warning("Warning: Payload is less than minimum", msg)
    in_endurance = min_endurance

max_alt_cruise = 1000  # CRUISE ALTITUDE
min_alt_cruise = 100
default_alt_cruise = 300
in_alt_cruise = df.iloc[2]['Value']
if numpy.isnan(in_alt_cruise):
    print("Cruise altitude unspecified")
    in_alt_cruise = default_alt_cruise
elif in_alt_cruise > max_alt_cruise:
    msg = "Cruise altitude cannot be more than " + str(max_alt_cruise) + " meters. "\
          "Cruise altitude will be set to " + str(max_alt_cruise) + " meters."
    generate_warning("Warning: Cruise altitude exceeds maximum", msg)
    in_alt_cruise = max_alt_cruise
elif in_alt_cruise < min_alt_cruise:
    msg = "Cruise altitude cannot be less than " + str(min_alt_cruise) + " meters. " \
          "Cruise altitude will be set to " + str(min_alt_cruise) + " meters."
    generate_warning("Warning: Cruise altitude is less than minimum", msg)
    in_alt_cruise = min_alt_cruise

max_v_cruise = 50  # CRUISE SPEED
min_v_cruise = 10
default_v_cruise = 15
in_v_cruise = df.iloc[3]['Value']
if numpy.isnan(in_v_cruise):
    print("Cruise velocity unspecified")
    in_v_cruise = default_v_cruise
elif in_v_cruise > max_v_cruise:
    msg = "Cruise speed cannot be more than " + str(max_v_cruise) + " m/s. "\
          "Cruise speed will be set to " + str(max_v_cruise) + " m/s."
    generate_warning("Warning: Cruise speed exceeds maximum", msg)
    in_v_cruise = max_v_cruise
elif in_v_cruise < min_v_cruise:
    msg = "Cruise speed cannot be less than " + str(min_v_cruise) + " m/s. " \
          "Cruise speed will be set to " + str(min_v_cruise) + " m/s."
    generate_warning("Warning: Cruise speed is less than minimum", msg)
    in_v_cruise = min_v_cruise

max_wing_loading = 3.05  # WING LOADING
min_wing_loading = 1.83
default_wing_loading = 3
in_wing_loading = df.iloc[4]['Value']
if numpy.isnan(in_wing_loading):
    in_wing_loading = default_wing_loading
elif in_wing_loading > max_wing_loading:
    msg = "Wing loading cannot be more than " + str(max_wing_loading) + " kg/m2. "\
          "Wing loading will be set to " + str(max_wing_loading) + " kg/m2."
    generate_warning("Warning: Wing loading exceeds maximum", msg)
    in_wing_loading = max_wing_loading
elif in_wing_loading < min_wing_loading:
    msg = "Wing loading cannot be less than " + str(min_wing_loading) + " kg/m2. " \
          "Wing loading will be set to " + str(min_wing_loading) + " kg/m2."
    generate_warning("Warning: Wing loading is less than minimum", msg)
    in_wing_loading = min_wing_loading

max_aspect_ratio = 9  # ASPECT RATIO
min_aspect_ratio = 5
default_aspect_ratio = 7
in_aspect_ratio = df.iloc[5]['Value']
if numpy.isnan(in_aspect_ratio):
    in_aspect_ratio = default_aspect_ratio
elif in_aspect_ratio > max_aspect_ratio:
    msg = "Aspect ratio cannot be more than " + str(max_aspect_ratio) + ". "\
          "Aspect ratio will be set to " + str(max_aspect_ratio) + "."
    generate_warning("Warning: Aspect ratio exceeds maximum", msg)
    in_aspect_ratio = max_aspect_ratio
elif in_aspect_ratio < min_aspect_ratio:
    msg = "Aspect ratio cannot be less than " + str(min_aspect_ratio) + ". " \
          "Aspect ratio will be set to " + str(min_aspect_ratio) + "."
    generate_warning("Warning: Aspect ratio is less than minimum", msg)
    in_aspect_ratio = min_aspect_ratio

max_taper_ratio = 0.7  # TAPER RATIO
min_taper_ratio = 0.3
default_taper_ratio = 0.5
in_taper_ratio = df.iloc[6]['Value']
if numpy.isnan(in_taper_ratio):
    in_taper_ratio = default_taper_ratio
elif in_taper_ratio > max_taper_ratio:
    msg = "Taper ratio cannot be more than " + str(max_taper_ratio) + ". "\
          "Taper ratio will be set to " + str(max_taper_ratio) + "."
    generate_warning("Warning: Taper ratio exceeds maximum", msg)
    in_taper_ratio = max_taper_ratio
elif in_taper_ratio < min_taper_ratio:
    msg = "Taper ratio cannot be less than " + str(min_taper_ratio) + ". " \
          "Taper ratio will be set to " + str(min_taper_ratio) + "."
    generate_warning("Warning: Taper ratio is less than minimum", msg)
    in_taper_ratio = min_taper_ratio

max_fuselage_ratio = 0.2  # FUSELAGE WIDTH/SPAN RATIO
min_fuselage_ratio = 0.08
default_fuselage_ratio = 0.14
in_fuselage_ratio = df.iloc[7]['Value']
if numpy.isnan(in_fuselage_ratio):
    in_fuselage_ratio = default_fuselage_ratio
elif in_fuselage_ratio > max_fuselage_ratio:
    msg = "Fuselage ratio cannot be more than " + str(max_fuselage_ratio) + ". "\
          "Fuselage ratio will be set to " + str(max_fuselage_ratio) + "."
    generate_warning("Warning: Fuselage ratio exceeds maximum", msg)
    in_fuselage_ratio = max_fuselage_ratio
elif in_fuselage_ratio < min_fuselage_ratio:
    msg = "Fuselage ratio cannot be less than " + str(min_fuselage_ratio) + ". " \
          "Fuselage ratio will be set to " + str(min_fuselage_ratio) + "."
    generate_warning("Warning: Fuselage ratio is less than minimum", msg)
    in_fuselage_ratio = min_fuselage_ratio

max_le_sweep = 30  # LEADING EDGE SWEEP ANGLE
min_le_sweep = 15
default_le_sweep = 25
in_le_sweep = df.iloc[8]['Value']
if numpy.isnan(in_le_sweep):
    in_le_sweep = default_le_sweep
elif in_le_sweep > max_le_sweep:
    msg = "LE sweep angle cannot be more than " + str(max_le_sweep) + " degrees. "\
          "LE sweep angle will be set to " + str(max_le_sweep) + " degrees."
    generate_warning("Warning: LE sweep angle exceeds maximum", msg)
    in_le_sweep = max_le_sweep
elif in_le_sweep < min_le_sweep:
    msg = "LE sweep angle cannot be less than " + str(min_le_sweep) + " degrees. " \
          "LE sweep angle will be set to " + str(min_le_sweep) + " degrees."
    generate_warning("Warning: LE sweep angle is less than minimum", msg)
    in_le_sweep = min_le_sweep

max_twist = 2  # TIP SECTION TWIST ANGLE
min_twist = -4
default_twist = -2
in_twist = df.iloc[9]['Value']
if numpy.isnan(in_twist):
    in_twist = default_twist
elif in_twist > max_twist:
    msg = "Twist angle cannot be more than " + str(max_twist) + " degrees. "\
          "Twist angle will be set to " + str(max_twist) + " degrees."
    generate_warning("Warning: Twist angle exceeds maximum", msg)
    in_twist = max_twist
elif in_twist < min_twist:
    msg = "Twist angle cannot be less than " + str(min_twist) + " degrees. " \
          "Twist angle will be set to " + str(min_twist) + " degrees."
    generate_warning("Warning: Twist angle is less than minimum", msg)
    in_twist = min_twist

# CLASS DEFINITION ================================================================


class Aircraft(GeomBase):

    # main inputs
    payload = Input(in_payload, validator=Range(min_payload, max_payload))
    endurance = Input(in_endurance, validator=Range(min_endurance, max_endurance))
    cruise_alt = Input(in_alt_cruise, validator=Range(min_alt_cruise, max_alt_cruise))
    cruise_v = Input(in_v_cruise, validator=Range(min_v_cruise, max_v_cruise))
    wing_loading = Input(in_wing_loading, validator=Range(min_wing_loading, max_wing_loading))
    aspect_ratio = Input(in_aspect_ratio, validator=Range(min_aspect_ratio, max_aspect_ratio))
    taper_ratio = Input(in_taper_ratio, validator=Range(min_taper_ratio, max_taper_ratio))
    fu_width_ratio = Input(in_fuselage_ratio, validator=Range(min_fuselage_ratio, max_fuselage_ratio))
    sweep = Input(in_le_sweep, validator=Range(min_le_sweep, max_le_sweep))
    twist = Input(in_twist, validator=Range(min_twist, max_twist))

    airfoil_root = Input("hs522")  # root & tip airfoil geometry
    airfoil_tip = Input("hs522")
    t_factor_root = Input(2, validator=Range(1, 3))  #: to reduce/increase airfoil thickness
    t_factor_tip = Input(1, validator=Range(1, 3))

    wing_dihedral = Input(0, validator=Range(-5, 5))
    cruise_aoa = Input(1, validator=Range(-7, 7))

    mot_r = Input(0.021)  # motor radius
    mot_t = Input(0.048)  # motor thickness

# ATTRIBUTES ======================================================================

    @Attribute
    def mtow_ratio(self):
        return M1*self.endurance+C1

    @Attribute
    def mtow(self):
        return self.payload*self.mtow_ratio

    @Attribute
    def wing_area(self):
        return self.mtow/self.wing_loading

    @Attribute
    def full_span(self):
        return sqrt(self.aspect_ratio*self.wing_area)

    @Attribute
    def fu_width(self):
        return self.full_span*self.fu_width_ratio

    @Attribute
    def w_semi_span(self):
        return (self.full_span-self.fu_width)/2

    @Attribute
    def w_c_root(self):
        return self.wing_area/(self.full_span*((1+self.taper_ratio)*(1-self.fu_width_ratio)/2+self.fu_width_ratio))

    @Attribute
    def w_c_tip(self):
        return self.w_c_root*self.taper_ratio

    @Attribute
    def mac_c(self):
        return self.w_c_root*(2/3)*((1+self.taper_ratio+self.taper_ratio**2)/(1+self.taper_ratio))

    @Attribute
    def mac_y(self):
        xp = [self.w_c_tip, self.w_c_root]
        fp = [self.w_semi_span, 0]
        return numpy.interp(self.mac_c, xp, fp)

    @Attribute
    def mac_x(self):
        return self.mac_y*tan(radians(self.sweep))

    @Attribute
    def cruise_rho(self):
        xp = [0, 1000]
        fp = [1.225, 1.112]
        return numpy.interp(self.cruise_alt, xp, fp)

    @Attribute
    def cruise_mu(self):
        xp = [0, 1000]
        fp = [0.00001789, 0.00001758]
        return numpy.interp(self.cruise_alt, xp, fp)

    @Attribute
    def cruise_cl(self):
        return self.mtow*GR/(0.5 * self.cruise_rho * self.cruise_v ** 2 * self.wing_area)

    @Attribute
    def cruise_re(self):
        return self.cruise_rho*self.cruise_v*self.mac_c/self.cruise_mu

    @Attribute
    def cruise_ma(self):
        cruise_temp = T_REF + (A * self.cruise_alt)
        return self.cruise_v/sqrt(KA * R * cruise_temp)

    @Attribute
    def mot_mount_s(self):
        return self.mot_r*2*1.1

    @Attribute
    def mot_mount_t(self):
        return self.w_c_root*0.75

    @Attribute  # Q3D
    def run_q3d(self):
        MATLAB_Q3D_ENGINE.cd(r'..\Q3D')

        x1 = 0  # section 1
        y1 = 0
        z1 = 0
        c1 = self.w_c_root
        t1 = 0

        x2 = 0.001  # section 2
        y2 = self.fu_width/2
        z2 = 0
        c2 = self.w_c_root
        t2 = 0

        x3 = self.w_semi_span*tan(radians(self.sweep))  # section 3
        y3 = self.fu_width/2+self.w_semi_span
        z3 = 0
        c3 = self.w_c_tip
        t3 = self.twist

        return MATLAB_Q3D_ENGINE.run_q3d(
            matlab.double([[x1, y1, z1, c1, t1],
                           [x2, y2, z2, c2, t2],
                           [x3, y3, z3, c3, t3]
                           ]),
            matlab.double([0]),  # incidence angle
            matlab.double([[0],
                           [self.fu_width],
                           [1]
                           ]),
            matlab.double([self.cruise_v]),
            matlab.double([self.cruise_rho]),
            matlab.double([self.cruise_alt]),
            matlab.double([self.cruise_re]),
            matlab.double([self.cruise_ma]),
            matlab.double([self.cruise_aoa]),
            nargout=2
        )

    @Attribute
    def q3d_res(self) -> Dict:
        """q3d results"""
        return self.run_q3d[0]

    @Attribute
    def q3d_ac(self) -> Dict:
        """q3d inputs"""
        return self.run_q3d[1]

#    @Attribute
#    def wing_alpha(self) -> float:
#        return self.q3d_res["Alpha"]

    @Attribute
    def wing_cl(self) -> float:
        return self.q3d_res["CLwing"]

    @Attribute
    def wing_cd(self) -> float:
        return self.q3d_res["CDwing"]

    @Attribute
    def cog_body(self):
        return self.body.cog

    @Attribute
    def output_pdf(self):
        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp)
        file_timestamp = date_time.strftime("%Y%m%d_%H%M%S")
        full_timestamp = date_time.strftime("%Y-%m-%d %H:%M:%S")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        pdf.cell(200, 4, txt="Generated: " + full_timestamp + "    ", ln=1, align="R")
        pdf.set_font("Courier", "B", size=14)
        pdf.cell(200, 10, txt="DESIGN REPORT", ln=1, align="C")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Input Parameters", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- Payload Weight       : " + str(self.payload) + " kg\n"
                               "- Endurance            : " + str(self.endurance) + " minutes\n"
                               "- Cruise Altitude      : " + str(self.cruise_alt) + " meters\n"
                               "- Cruise Speed         : " + str(self.cruise_v) + " m/s\n"
                               "- Wing Loading         : " + str(self.wing_loading) + " kg/m2\n"
                               "- Aspect Ratio         : " + str(self.aspect_ratio) + "\n"
                               "- Taper Ratio          : " + str(self.taper_ratio) + "\n"
                               "- Fuselage Width Ratio : " + str(self.fu_width_ratio)+"\n"
                               "- LE Sweep Angle       : " + str(self.sweep) + " degrees\n"
                               "- Twist Angle          : " + str(self.twist) + " degrees\n")
        pdf.output("report_" + file_timestamp + ".pdf")
        return "Report generated. Filename: report_" + file_timestamp + ".pdf"

# PARTS ===========================================================================

    @Part
    def aircraft_frame(self):
        return Frame(pos=self.position,
                     hidden=True)

    @Part
    def right_wing(self):
        return LiftingSurface(
            pass_down="airfoil_root, airfoil_tip, w_c_root, w_c_tip,"
                      "t_factor_root, t_factor_tip, w_semi_span, "
                      "sweep, twist",
            position=translate(self.position, 'y', self.fu_width / 2),
            mesh_deflection=0.0001,
            color="white"
        )

    @Part
    def left_wing(self):
        return MirroredShape(
            shape_in=self.right_wing,
            reference_point=self.position,
            vector1=self.position.Vz,
            vector2=self.position.Vx,
            mesh_deflection=0.0001,
            color="white"
        )

    @Part
    def body(self):
        return LiftingSurface(
            w_c_root=self.w_c_root,
            w_c_tip=self.w_c_root,
            airfoil_root=self.airfoil_root,
            airfoil_tip=self.airfoil_root,
            t_factor_root=self.t_factor_root,
            t_factor_tip=self.t_factor_root,
            w_semi_span=self.fu_width,
            sweep=0,
            twist=0,
            position=translate(self.position, 'y', -1 * self.fu_width / 2),
            mesh_deflection=0.0001,
            color="white"
        )

    @Part
    def motor_mount_box(self):
        return Box(
            height=self.mot_mount_s,
            length=self.mot_mount_s,
            width=self.mot_mount_t,
            position=translate(self.position,
                               'y', -1 * self.mot_mount_s / 2,
                               'x', self.w_c_root - self.mot_mount_t),
            color="white",
            hidden=True)

    @Part
    def motor_mount(self):
        return SubtractedSolid(shape_in=self.motor_mount_box,
                               tool=self.body,
                               color="white")

    @Part
    def motor(self):
        return Cylinder(
            radius=self.mot_r,
            height=self.mot_t,
            angle=pi*2,
            position=rotate90(translate(self.position,
                                        'x', self.w_c_root,
                                        'z', self.mot_r*1.1),
                              'y'),
            color="orange"
        )

    @Part
    def aircraft_solid(self):
        return Fused(
            shape_in=self.body,
            tool=[self.left_wing,
                  self.right_wing,
                  self.motor,
                  self.motor_mount],
            mesh_deflection=0.0001,
            color="white",
            hidden=True
        )

    @Part
    def step_writer_components(self):
        return STEPWriter(
            default_directory=DIR,
            nodes=[self.body,
                   self.left_wing,
                   self.right_wing,
                   self.motor,
                   self.motor_mount]
        )

    @Part
    def step_writer_fused(self):
        return STEPWriter(
            default_directory=DIR,
            nodes=[self.aircraft_solid]
        )


if __name__ == '__main__':
    from parapy.gui import display
    obj = Aircraft(label="aircraft")
    display(obj)
