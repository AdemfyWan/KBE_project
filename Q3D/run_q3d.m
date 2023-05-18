function [Res, AC] = run_q3d(planform, inc, sections, v, rho, alt, re, ma, alpha)

   % Wing planform geometry
   %                x    y     z   chord(m)    twist angle (deg)
%   AC.Wing.Geom = [0     0     0     3.5         0;
%                   0.9  14.5   0     1.4         0];
   AC.Wing.Geom = planform

   % Wing incidence angle (degree)
%   AC.Wing.inc  = 0;
   AC.Wing.inc  = inc;

   % Airfoil coefficients input matrix
   %                    | ->     upper curve coeff.                <-|   | ->       lower curve coeff.       <-|
   AC.Wing.Airfoils   = [0.2171    0.3450    0.2975    0.2685    0.2893  -0.1299   -0.2388   -0.1635   -0.0476    0.0797;
                         0.2171    0.3450    0.2975    0.2685    0.2893  -0.1299   -0.2388   -0.1635   -0.0476    0.0797;
                         0.2171    0.3450    0.2975    0.2685    0.2893  -0.1299   -0.2388   -0.1635   -0.0476    0.0797];

 %  AC.Wing.eta = [0;0.2;1];  % Spanwise location of the airfoil sections
   AC.Wing.eta = sections

   % Viscous vs inviscid
   AC.Visc  = 1;              % 0 for inviscid and 1 for viscous analysis
   AC.Aero.MaxIterIndex = 150;    %Maximum number of Iteration for the
                                   %convergence of viscous calculation

   % Flight Condition
   AC.Aero.V     = v;            % flight speed (m/s)
   AC.Aero.rho   = rho;         % air density  (kg/m3)
   AC.Aero.alt   = alt;             % flight altitude (m)
   AC.Aero.Re    = re;        % reynolds number (based on mean aerodynamic chord)
   AC.Aero.M     = ma;           % flight Mach number
   % AC.Aero.CL    = 0.2195;          % lift coefficient - comment this line to run the code for given alpha%
   AC.Aero.Alpha = alpha;             % angle of attack -  comment this line to run the code for given cl

   %%
   tic

   Res = Q3D_solver(AC);

   toc

end