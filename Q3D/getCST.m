function [CST] = getCST(rootairfoil, tipairfoil, Troot, Ttip)

% clc
% clear
% close all
% 
% rootairfoil = "hs522";
% tipairfoil = "hs522";
% Troot = 2; % thickness factor
% Ttip = 1;

    global airfoil;
    
    airfoil.root  = rootairfoil;
    airfoil.tip   = tipairfoil;
    airfoil.Troot = Troot;
    airfoil.Ttip  = Ttip;
    
    M       = 10; % number of CST-coefficients in design-vector x
    M_break = M/2;
    n       = 200;
    X_vect  = linspace(0,1,n)';  % points for evaluation along x-axis
    x0      = 0*ones(M,1);  % initial value of design vector x (starting vector for search process)
    lb      = -1*ones(M,1); % lower bound vector of x
    ub      = 1*ones(M,1);  % upper bound vector of x
    
    options = optimset('Display','final');

    fprintf('\n');
    fprintf('CALCULATING ROOT AIRFOIL CST COEFFICIENTS ...');
    fprintf('\n');
    [x_root,~,~] = fmincon(@CST_objective_root,x0,[],[],[],[],lb,ub,[],options);
    
    fprintf('\n');
    fprintf('CALCULATING TIP AIRFOIL CST COEFFICIENTS ...');
    fprintf('\n');
    [x_tip,~,~] = fmincon(@CST_objective_tip,x0,[],[],[],[],lb,ub,[],options);
    
    CST(1,:)=x_root';
    CST(2,:)=CST(1,:);
    CST(3,:)=x_tip;

end

% Plot CST fit (testing)
% 
% CSTa=x_root(1:M_break);
% CSTb=x_root(1+M_break:end);
% [Xtu_root_ref,Xtl_root_ref,C_root_ref,Thu_root_ref,Thl_root_ref,Cm_root_ref] = D_airfoil2(CSTa,CSTb,X_vect);
% 
% CSTc=x_tip(1:M_break);
% CSTd=x_tip(1+M_break:end);
% [Xtu_tip_ref,Xtl_tip_ref,C_tip_ref,Thu_tip_ref,Thl_tip_ref,Cm_tip_ref] = D_airfoil2(CSTc,CSTd,X_vect);
% 
% mydir  = pwd;
% idcs   = strfind(mydir,'\');
% newdir = mydir(1:idcs(end)-1)+"\AssignmentMain\Airfoils\";
% 
% 
% fid= fopen(newdir+rootairfoil+'.dat','r'); % Filename can be changed as required
% Coor_root = fscanf(fid,'%g %g',[2 Inf]) ; 
% Coor_root(2,:) = Coor_root(2,:)*Troot;
% fclose(fid) ; 
% fid= fopen(newdir+tipairfoil+'.dat','r'); % Filename can be changed as required
% Coor_tip = fscanf(fid,'%g %g',[2 Inf]) ; 
% Coor_tip(2,:) = Coor_tip(2,:)*Ttip;
% fclose(fid) ;
% 
% figure ('Name','Airfoils')
% tiledlayout(2,1);
% nexttile
% hold on
% plot(Xtu_root_ref(:,1),Xtu_root_ref(:,2),'b');    %plot upper surface coords
% af_ref1=plot(Xtl_root_ref(:,1),Xtl_root_ref(:,2),'b');    %plot lower surface coords
% af_ref0=plot(Coor_root(1,:),Coor_root(2,:),'rx');
% %     axis([0,1,-0.18,0.18]);
% axis equal
% title('Root Airfoil')
% xlabel('x/c')
% ylabel('z/c')
% nexttile
% hold on
% plot(Xtu_tip_ref(:,1),Xtu_tip_ref(:,2),'b');    %plot upper surface coords
% plot(Xtl_tip_ref(:,1),Xtl_tip_ref(:,2),'b');    %plot lower surface coords
% plot(Coor_tip(1,:),Coor_tip(2,:),'rx')
% %     axis([0,1,-0.18,0.18]);
% axis equal
% title('Tip Airfoil')
% xlabel('x/c')
% ylabel('z/c')
% lgd1=legend([af_ref0 af_ref1],{'Reference Coordinates','CST Fitting'});
% lgd1.Layout.Tile = 'south';


