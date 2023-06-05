
from math import tan, radians, sqrt
from parapy.core import *
from parapy.core.validate import Range
from parapy.geom import *
from ref_frame import Frame
from typing import Dict
from parapy.exchange import STEPWriter
from fpdf import FPDF
from datetime import datetime
from AssignmentMain import MATLAB_Q3D_ENGINE
import matlab.engine
import pandas as pd
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from bodyassembly import BodyAssembly
from motorassembly import MotorAssembly
from wingassembly import WingAssembly
from battery import Battery
from payload import Payload

DIR = os.path.dirname(__file__)


def generate_warning(warning_header, msg):
    from tkinter import Tk, messagebox
    window = Tk()  # initialization
    window.withdraw()
    messagebox.showwarning(warning_header, msg)  # generates message box
    window.deiconify()  # kills the gui
    window.destroy()
    window.quit()


# TIMESTAMP ============================================================================================================

timestamp = time.time()
date_time = datetime.fromtimestamp(timestamp)
file_timestamp = date_time.strftime("%Y%m%d_%H%M%S")
full_timestamp = date_time.strftime("%Y-%m-%d %H:%M:%S")

# CONSTANTS ============================================================================================================

GR = 9.80665  # standard gravity
KA = 1.4  # specific heat ratio, air
R = 287  # gas constant (J/kg K)
A = -0.0065  # ISA temperature lapse rate up to alt=11km
T_REF = 288  # reference temperature (K)
M1 = 0.01849557883  # MTOW vs payload ratio function, slope
C1 = 3.769488083  # y-intercept

# READ & VALIDATE INPUT FILE ===========================================================================================

df = pd.read_excel('input.xlsx')

max_payload = 4   # PAYLOAD
min_payload = 0.1
default_payload = 0.5
in_payload = df.iloc[0]['Value']
if np.isnan(in_payload):
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
if np.isnan(in_endurance):
    print("Endurance unspecified")
    in_endurance = default_endurance
elif in_endurance > max_endurance:
    msg = "Endurance cannot be more than " + str(max_endurance) + " minutes. "\
          "Endurance will be set to " + str(max_endurance) + " minutes."
    generate_warning("Warning: Endurance exceeds maximum", msg)
    in_endurance = max_endurance
elif in_endurance < min_endurance:
    msg = "Endurance cannot be less than " + str(min_endurance) + " minutes. " \
          "Endurance will be set to " + str(min_endurance) + " minutes."
    generate_warning("Warning: Endurance is less than minimum", msg)
    in_endurance = min_endurance

max_alt_cruise = 1000  # CRUISE ALTITUDE
min_alt_cruise = 100
default_alt_cruise = 300
in_alt_cruise = df.iloc[2]['Value']
if np.isnan(in_alt_cruise):
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
if np.isnan(in_v_cruise):
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
if np.isnan(in_wing_loading):
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
min_aspect_ratio = 4
default_aspect_ratio = 7
in_aspect_ratio = df.iloc[5]['Value']
if np.isnan(in_aspect_ratio):
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
if np.isnan(in_taper_ratio):
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
if np.isnan(in_fuselage_ratio):
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

max_le_sweep = 40  # LEADING EDGE SWEEP ANGLE
min_le_sweep = 15
default_le_sweep = 25
in_le_sweep = df.iloc[8]['Value']
if np.isnan(in_le_sweep):
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
if np.isnan(in_twist):
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

# CLASS DEFINITION & INPUTS ============================================================================================


class Aircraft(GeomBase):

    # main inputs
    payload_weight = Input(in_payload, validator=Range(min_payload, max_payload))
    endurance = Input(in_endurance, validator=Range(min_endurance, max_endurance))
    cruise_alt = Input(in_alt_cruise, validator=Range(min_alt_cruise, max_alt_cruise))
    cruise_v = Input(in_v_cruise, validator=Range(min_v_cruise, max_v_cruise))
    wing_loading = Input(in_wing_loading, validator=Range(min_wing_loading, max_wing_loading))
    aspect_ratio = Input(in_aspect_ratio, validator=Range(min_aspect_ratio, max_aspect_ratio))
    taper_ratio = Input(in_taper_ratio, validator=Range(min_taper_ratio, max_taper_ratio))
    fu_width_ratio = Input(in_fuselage_ratio, validator=Range(min_fuselage_ratio, max_fuselage_ratio))
    sweep_le = Input(in_le_sweep, validator=Range(min_le_sweep, max_le_sweep))
    twist = Input(in_twist, validator=Range(min_twist, max_twist))

    airfoil_root = Input("hs522")  # root & tip airfoil geometry
    airfoil_tip = Input("hs522")
    t_factor_root = Input(2, validator=Range(1, 3))  #: to reduce/increase airfoil thickness
    t_factor_tip = Input(1, validator=Range(1, 2))

    #  propulsion system
    power_weight_ratio = Input(220, validator=Range(176, 264))

    #  propeller dimensions
    p_twist = Input(35)
    p_taper = Input(0.008/0.018)

    #    wing_dihedral = Input(0, validator=Range(-5, 5))
    #    cruise_aoa = Input(1, validator=Range(-7, 7))



# SIZING CALCULATIONS ==================================================================================================

    @Attribute
    def mtow_ratio(self):
        return M1*self.endurance+C1

    @Attribute
    def mtow(self):
        return self.payload_weight*self.mtow_ratio

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

# BODY, COMPARTMENT COVER, MOTOR MOUNT =================================================================================

    @Part
    def aircraft_frame(self):
        return Frame(pos=self.position,
                     hidden=True)

    @Part
    def body_assembly(self):
        return BodyAssembly(
            w_c_root=self.w_c_root,
            t_factor_root=self.t_factor_root,
            airfoil_root=self.airfoil_root,
            fu_width=self.fu_width,
            sweep_le=self.sweep_le,
            w_semi_span=self.w_semi_span,
            motor_radius=self.motor_assembly.motor_radius
        )

# WINGS, ELEVONS, WINGLETS =============================================================================================

    @Part
    def wing_assembly(self):
        return WingAssembly(
            w_c_root=self.w_c_root,
            w_c_tip=self.w_c_tip,
            airfoil_root=self.airfoil_root,
            airfoil_tip=self.airfoil_tip,
            t_factor_root=self.t_factor_root,
            t_factor_tip=self.t_factor_tip,
            w_semi_span=self.w_semi_span,
            sweep_le=self.sweep_le,
            twist=self.twist,
            fu_width=self.fu_width
        )

# MOTOR & PROPELLER ====================================================================================================

    @Part
    def motor_assembly(self):
        return MotorAssembly(
            w_c_root=self.w_c_root,
            airfoil_prop=self.airfoil_root,
            power_weight_ratio=self.power_weight_ratio,
            mtow=self.mtow,
            position=translate(self.position,
                               'x', self.w_c_root)
        )

# PAYLOAD & BATTERY ====================================================================================================

    @Part
    def payload(self):
        return Payload(
            w_c_root=self.w_c_root,
            t_factor=self.t_factor_root,
            fu_width=self.fu_width,
            payload_weight=self.payload_weight,
            airfoil_name=self.airfoil_root,
            position=translate(self.position,
                               'x', self.w_c_root * 0.1 + self.payload.width / 2 + 0.01,
                               'z', self.payload.height/2),
            centered=True,
            color="Red",
            hidden=False)

    @Part
    def battery(self):
        return Battery(
            endurance=self.endurance,
            v_cruise=self.cruise_v,
            ref_area=self.wing_area,
            cd=self.wing_cd,
            air_density=self.cruise_rho,
            position=translate(self.position,
                               'x', self.payload.position[0] + self.payload.width / 2 + self.battery.width / 2 + 0.005,
                               'z', self.battery.height/2),
            centered=True,
            color="Blue",
            hidden=False)

# Q3D ==================================================================================================================

    @Attribute
    def cruise_rho(self):
        xp = [0, 1000]
        fp = [1.225, 1.112]
        return np.interp(self.cruise_alt, xp, fp)

    @Attribute
    def cruise_mu(self):
        xp = [0, 1000]
        fp = [0.00001789, 0.00001758]
        return np.interp(self.cruise_alt, xp, fp)

    @Attribute
    def cruise_cl(self):
        return self.mtow * GR / (0.5 * self.cruise_rho * self.cruise_v ** 2 * self.wing_area)

    @Attribute
    def cruise_re(self):
        return self.cruise_rho * self.cruise_v * self.mac_c / self.cruise_mu

    @Attribute
    def cruise_ma(self):
        cruise_temp = T_REF + (A * self.cruise_alt)
        return self.cruise_v / sqrt(KA * R * cruise_temp)

    @Attribute
    def run_q3d(self):
        MATLAB_Q3D_ENGINE.cd(r'..\Q3D')

        x1 = 0  # section 1
        y1 = 0
        z1 = 0
        c1 = self.w_c_root
        t1 = 0

        x2 = 0.001  # section 2
        y2 = self.fu_width / 2
        z2 = 0
        c2 = self.w_c_root
        t2 = 0

        x3 = self.w_semi_span * tan(radians(self.sweep_le))  # section 3
        y3 = self.fu_width / 2 + self.w_semi_span
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
            matlab.double([self.cruise_cl]),
            self.airfoil_root,
            self.airfoil_tip,
            matlab.double([self.t_factor_root]),
            matlab.double([self.t_factor_tip]),
            nargout=2
        )

    @Attribute
    def q3d_res(self) -> Dict:
        return self.run_q3d[0]

    @Attribute
    def q3d_ac(self) -> Dict:
        return self.run_q3d[1]

    @Attribute
    def wing_alpha(self) -> float:
        return self.q3d_res["Alpha"]

    #    @Attribute
    #    def wing_cl(self) -> float:
    #        return self.q3d_res["CLwing"]

    @Attribute
    def wing_cd(self) -> float:
        return self.q3d_res["CDwing"]

    @Attribute
    def ld_ratio(self):
        return self.cruise_cl/self.wing_cd

# CG ANALYSIS ==========================================================================================================

    @Attribute
    def mac_c(self):
        return self.w_c_root*(2/3)*((1+self.taper_ratio+self.taper_ratio**2)/(1+self.taper_ratio))

    @Attribute
    def mac_y(self):
        xp = [self.w_c_tip, self.w_c_root]
        fp = [self.w_semi_span, 0]
        return np.interp(self.mac_c, xp, fp)

    @Attribute
    def mac_x(self):
        return self.mac_y*tan(radians(self.sweep_le))

    @Attribute
    def cg_airframe_x(self):
        x1 = self.body_assembly.main_body.cog[0]
        x2 = self.wing_assembly.main_wing.cog[0]
        vol1 = self.body_assembly.main_body.volume
        vol2 = self.wing_assembly.main_wing.volume
        return (x1*vol1 + 2*x2*vol2) / (vol1 + 2*vol2)

    @Attribute
    def airframe_weight(self):
        return self.mtow-(self.motor_assembly.motor_weight+self.payload_weight+self.battery.battery_weight)

    @Attribute
    def cg_overall_x(self):
        wp = self.payload_weight
        xp = self.payload.cog[0]
        wa = self.airframe_weight
        xa = self.cg_airframe_x
        wb = self.battery.battery_weight
        xb = self.battery.cog[0]
        wm = self.motor_assembly.motor_weight
        xm = self.motor_assembly.motor.cog[0]
        return (wp*xp + wa*xa + wb*xb + wm*xm)/self.mtow

    @Attribute
    def cg_analysis(self):
        tip_le_x_pos = self.w_semi_span * tan(radians(self.sweep_le))

        x_root = self.wing_assembly.main_wing.root_airfoil.x_points
        z_root = self.wing_assembly.main_wing.root_airfoil.z_points
        x_tip = [x + tip_le_x_pos for x in self.wing_assembly.main_wing.tip_airfoil.x_points]
        z_tip = self.wing_assembly.main_wing.tip_airfoil.z_points

        fig, ax = plt.subplots()

        plt.plot(x_root, z_root, color="gray", linewidth=0.5, label="Root and tip airfoils")
        plt.plot(x_tip, z_tip, color="gray", linewidth=0.5)
        plt.plot([self.mac_x, self.mac_x + self.mac_c], [0, 0], color="black", linewidth=2, label="MAC")
        plt.plot(self.mac_x + self.mac_c * 0.25, 0, marker="o", markersize=5, color="blue", label="AC")
        plt.plot(self.cg_overall_x, 0, marker="x", markersize=10, color="red", label="Overall CG")
        plt.legend(loc='upper right', prop={'size': 8}, frameon=False)
        plt.ylabel('z (m)')
        plt.xlabel('x (m)')
        plt.title('CG Analysis')

#        if self.cg_overall_x < self.mac_x + self.mac_c * 0.25:
#            txt = 'CG is in front of AC. Aircraft is longitudinally stable.'
#        else:
#            txt = 'CG is behind AC. Consider modifying geometric parameters (e.g. increase sweep)'
#        fig.text(.5, .025, txt, ha='center')

        ax.set_ylim(-0.25 * self.w_c_root / 0.4342, 0.25 * self.w_c_root / 0.4342)
        ax.set_aspect('equal')

        plt.savefig("Output/" + file_timestamp + "_cg_analysis.png")

        plt.show()
        return 1

# PDF REPORT ===========================================================================================================

    @Attribute
    def planform_plot(self):
        tip_le_x_pos = self.w_semi_span * tan(radians(self.sweep_le))

        fig, ax = plt.subplots()

        plt.plot([-self.fu_width/2, self.fu_width/2], [0, 0], color="black", linewidth=1)
        plt.plot([-self.fu_width/2, self.fu_width/2], [self.w_c_root, self.w_c_root], color="black", linewidth=1)
        plt.plot([-self.fu_width/2, -self.fu_width/2], [0, self.w_c_root], color="black", linewidth=1)
        plt.plot([self.fu_width/2, self.fu_width/2], [0, self.w_c_root], color="black", linewidth=1)
        plt.plot([self.fu_width/2, self.w_semi_span], [0, tip_le_x_pos], color="black", linewidth=1)
        plt.plot([self.w_semi_span, self.w_semi_span], [tip_le_x_pos, tip_le_x_pos+self.w_c_tip], color="black", linewidth=1)
        plt.plot([self.w_semi_span, self.fu_width/2], [tip_le_x_pos+self.w_c_tip, self.w_c_root], color="black", linewidth=1)
        plt.plot([-self.fu_width/2, -self.w_semi_span], [0, tip_le_x_pos], color="black", linewidth=1)
        plt.plot([-self.w_semi_span, -self.w_semi_span], [tip_le_x_pos, tip_le_x_pos+self.w_c_tip], color="black", linewidth=1)
        plt.plot([-self.w_semi_span, -self.fu_width/2], [tip_le_x_pos+self.w_c_tip, self.w_c_root], color="black", linewidth=1)
        plt.ylabel('x (m)')
        plt.xlabel('y (m)')
        plt.title('Planform')

        ax.set_aspect('equal')
        plt.gca().invert_yaxis()

        plt.savefig("Output/" + file_timestamp + "_planform.png")

        plt.show()
        return 1

    @Attribute
    def output_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        pdf.cell(200, 4, txt="Generated: " + full_timestamp + "    ", ln=1, align="R")
        pdf.set_font("Courier", "B", size=14)
        pdf.cell(200, 10, txt="DESIGN REPORT", ln=1, align="C")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Input Parameters", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- Payload Weight        : " + str(self.payload_weight) + " kg\n"
                               "- Endurance             : " + str(self.endurance) + " minutes\n"
                               "- Cruise Altitude       : " + str(self.cruise_alt) + " m\n"
                               "- Cruise Speed          : " + str(self.cruise_v) + " m/s\n"
                               "- Wing Loading          : " + str(self.wing_loading) + " kg/m2\n"
                               "- Aspect Ratio          : " + str(self.aspect_ratio) + "\n"
                               "- Taper Ratio           : " + str(self.taper_ratio) + "\n"
                               "- Fuselage Width Ratio  : " + str(self.fu_width_ratio) + "\n"
                               "- LE Sweep Angle        : " + str(self.sweep_le) + " deg\n"
                               "- Twist Angle           : " + str(self.twist) + " deg\n"
                               "- Root Airfoil          : " + self.airfoil_root + "\n"
                               "- Tip Airfoil           : " + self.airfoil_tip + "\n")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Calculated Parameters", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- MTOW/Payload Ratio    : " + str("{:.4f}".format(self.mtow_ratio)) + "\n"
                               "- MTOW                  : " + str("{:.4f}".format(self.mtow)) + " kg\n"
                               "- Airframe Weight       : " + str("{:.4f}".format(self.airframe_weight)) + " kg\n"
                               "- Wing Area             : " + str("{:.4f}".format(self.wing_area)) + " m2\n"
                               "- Full Span             : " + str("{:.4f}".format(self.full_span)) + " m\n"
                               "- Fuselage Width        : " + str("{:.4f}".format(self.fu_width)) + " m\n"
                               "- Wing-Only Semispan    : " + str("{:.4f}".format(self.w_semi_span)) + " m\n"
                               "- Root Chord            : " + str("{:.4f}".format(self.w_c_root)) + " m\n"
                               "- Tip Chord             : " + str("{:.4f}".format(self.w_c_tip)) + " m\n"
                               "- MAC                   : " + str("{:.4f}".format(self.mac_c)) + " m\n"
                               "- MAC LE X-Position     : " + str("{:.4f}".format(self.mac_x)) + " m\n")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Flight Conditions", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- Air Density           : " + str("{:.4f}".format(self.cruise_rho)) + " kg/m3\n"
                               "- Dynamic Viscosity     : " + str(self.cruise_mu) + " Ns/m2\n"
                               "- Reynolds Number       : " + str("{:.0f}".format(self.cruise_re)) + "\n"
                               "- Mach Number           : " + str("{:.4f}".format(self.cruise_ma)) + "\n"
                               "- Lift Coefficient      : " + str("{:.4f}".format(self.cruise_cl)) + "\n")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Q3D Analysis Results", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- Cruise AoA            : " + str("{:.4f}".format(self.wing_alpha)) + " deg\n"          
                               "- Drag Coefficient      : " + str("{:.4f}".format(self.wing_cd)) + "\n"
                               "- Lift-to-Drag Ratio    : " + str("{:.4f}".format(self.ld_ratio)) + "\n")
        pdf.set_font("Courier", "B", size=10)
        pdf.cell(200, 10, txt="Propulsion System Specifications", ln=1, align="L")
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(200, 4, "- Power-to-Weight Ratio : " + str("{:.0f}".format(self.power_weight_ratio)) + " W/kg\n"
                               "- Motor Power           : " + str("{:.4f}".format(self.motor_assembly.motor_power)) + " W\n"
                               "- Motor Weight          : " + str("{:.4f}".format(self.motor_assembly.motor_weight)) + " kg\n"
                               "- Battery Capacity      : " + str("{:.4f}".format(self.battery.battery_capacity)) + " Wh\n"
                               "- Battery Weight        : " + str("{:.4f}".format(self.battery.battery_weight)) + " kg\n")

        if self.planform_plot == 1:
            pdf.image("Output/" + file_timestamp + "_planform.png", 103, 25, 100)
        if self.cg_analysis == 1:
            pdf.image("Output/" + file_timestamp + "_cg_analysis.png", 103, 90, 100)
        if os.path.exists("Output/" + file_timestamp + "_report.pdf"):
            os.remove("Output/" + file_timestamp + "_report.pdf")
        pdf.output("Output/" + file_timestamp + "_report.pdf")
        return "Report generated. Filename: " + file_timestamp + "_report.pdf"

#  STEP WRITER =========================================================================================================

    @Part
    def aircraft_solid(self):
        return Fused(
            shape_in=self.body_assembly.main_body,
            tool=[self.body_assembly.compartment_cover,
                  self.body_assembly.motor_mount,
                  self.wing_assembly.wing_right,
                  self.wing_assembly.wing_left,
                  self.wing_assembly.elevon_right,
                  self.wing_assembly.elevon_left,
                  self.wing_assembly.winglet.winglet_right,
                  self.wing_assembly.winglet.winglet_left,
                  self.motor_assembly.motor,
                  self.motor_assembly.propeller.propeller_hub,
                  self.motor_assembly.propeller.propeller_blade_right,
                  self.motor_assembly.propeller.propeller_blade_left,
                  self.payload,
                  self.battery],
            mesh_deflection=0.0001,
            color="white",
            hidden=True
        )

    @Part
    def step_writer_components(self):
        return STEPWriter(
            default_directory=DIR + "/Output",
            nodes=[self.body_assembly.main_body,
                   self.body_assembly.compartment_cover,
                   self.body_assembly.motor_mount,
                   self.wing_assembly.wing_right,
                   self.wing_assembly.wing_left,
                   self.wing_assembly.elevon_right,
                   self.wing_assembly.elevon_left,
                   self.wing_assembly.winglet.winglet_right,
                   self.wing_assembly.winglet.winglet_left,
                   self.motor_assembly.motor,
                   self.motor_assembly.propeller.propeller_hub,
                   self.motor_assembly.propeller.propeller_blade_right,
                   self.motor_assembly.propeller.propeller_blade_left,
                   self.payload,
                   self.battery]
        )

    @Part
    def step_writer_fused(self):
        return STEPWriter(
            default_directory=DIR + "/Output",
            nodes=[self.aircraft_solid]
        )


if __name__ == '__main__':
    from parapy.gui import display
    obj = Aircraft(label="aircraft")
    display(obj)
