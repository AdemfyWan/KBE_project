from parapy.core import *
from parapy.geom import *
from math import radians


class Winglet(GeomBase):
    chord = Input(1)
    winglet_thickness = Input(0.005)
    xpos = Input(0)
    ypos = Input(0)

#    @Input
#    def winglet_length(self):
#        return self.chord*1.5

    @Attribute
    def winglet_length(self):
        return self.chord*1.5

    @Attribute
    def winglet_height(self):
        return self.winglet_length/2.7

    @Part
    def tip_airfoil(self):
        return Rectangle(width=self.chord,
                         length=self.chord*0.12,
                         color="blue",
                         hidden=True)

    @Part
    def winglet_line_segment1(self):
        return LineSegment(start=Point(-0.4, 0, 0),
                           end=Point(0.05, -0.175, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_line_segment2(self):
        return LineSegment(start=Point(0.05, -0.175, 0),
                           end=Point(0.6, -0.175, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_line_segment3(self):
        return LineSegment(start=Point(0.6, -0.175, 0),
                           end=Point(0.35, 0, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_line_segment4(self):
        return LineSegment(start=Point(0.35, 0, 0),
                           end=Point(0.6, 0.35, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_line_segment5(self):
        return LineSegment(start=Point(0.6, 0.35, 0),
                           end=Point(0.05, 0.35, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_line_segment6(self):
        return LineSegment(start=Point(0.05, 0.35, 0),
                           end=Point(-0.4, 0, 0),
                           color="red",
                           hidden=True)

    @Part
    def winglet_profile_unscaled(self):
        return ComposedCurve(built_from=[self.winglet_line_segment1,
                                         self.winglet_line_segment2,
                                         self.winglet_line_segment3,
                                         self.winglet_line_segment4,
                                         self.winglet_line_segment5,
                                         self.winglet_line_segment6],
                             position=rotate90(self.position, "x"),
                             line_thickness=2,
                             color="yellow",
                             hidden=True)

    @Part
    def winglet_profile(self):
        return ScaledCurve(curve_in=self.winglet_profile_unscaled,
                           reference_point=Point(0, 0, 0),
                           factor=self.winglet_length,
                           color="green",
                           hidden=True)

    @Part
    def winglet_extrude(self):
        return ExtrudedSolid(island=self.winglet_profile,
                             distance=self.winglet_thickness,
                             direction=(0, 0, 1),
                             hidden=True)

    @Part
    def winglet_rotated(self):
        return RotatedShape(shape_in=self.winglet_extrude,
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            hidden=True
                            )

    @Part
    def winglet_right(self):
        return TranslatedShape(shape_in=self.winglet_rotated,
                               displacement=Vector(self.xpos,
                                                   self.ypos,
                                                   0),
                               color="white",
                               hidden=False
                               )

    @Part
    def winglet_left(self):
        return MirroredShape(
            shape_in=self.winglet_right,
            reference_point=self.position,
            vector1=self.position.Vz,
            vector2=self.position.Vx,
            mesh_deflection=0.0001,
            color="white"
        )


if __name__ == '__main__':
    from parapy.gui import display

    obj = Winglet()
    display(obj)
