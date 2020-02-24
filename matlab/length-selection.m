% Theoretical minimum motor resolution code

% For any given car orientation we can specify a position, and an angle. We
% can represent this by a dual space: a position vector and an orientation
% vector at that position. The origin of our dual space will be the base of
% the robot, centered with respect to the workspace and 0.25 m back. The
% x-direction is along the long edge of the workspace. The y-direction is
% forwards along the short edge. The car can yaw from 45 to -45 degrees.
% The possible ranges of values of the charger port position are 

% 1. -0.5 to 0.5 in the x-direction
% 2. 0.25 to 0.75 in the y-direction
% 3. -pi/4 to pi/4 in the yaw 

syms specposx specposy specangle

% We will solve this along a 1 mm x 1 mm x 1 deg grid, or 1000 * 500 * 90 =
% 4,500,000 points, then find the smallest difference in angles. 

% The robot's geometry is given by three angles (q1, q2, q3) and three
% lengths (l1 = 0.5m, l2 = 0.5m, l3 = 0.1m). Some observations on the
% motion, which make this problem significantly easier to solve:

l1 = 0.5;
l2 = 0.5;
l3 = 0.1;
syms q1 q2 q3;

% If we want the final joint and length to be pointing towards the charging
% port, we need the other two joints to have an 'end effector' position
% -0.1 m in the direction of the angle of the car. Therefore, we can solve
% for the position like we're dealing with a 2-jointed planar robot, which
% is much easier. 

% The position of the 2 long joints is:
initx = l1 *cos(q1) + l2 * cos(q2 + q1);
inity = l1 * sin(q1) + l2 * sin(q2 + q1);
% The final position must be calculated from the position vector
finalx = specposx - l3 * cos(specangle);
finaly = specposy - l3 * sin(specangle);

eqnx = initx == finalx;
eqny = inity == finaly;
S = solve([eqnx eqny], [q1 q2]);
q1calcL = matlabFunction(S.q1(1),'Vars',[specposx specposy specangle]);
q2calcL = matlabFunction(S.q2(1),'Vars',[specposx specposy specangle]);

q1calcR = matlabFunction(S.q1(2),'Vars',[specposx specposy specangle]);
q2calcR = matlabFunction(S.q2(2),'Vars',[specposx specposy specangle]);

disp(q1calc(0.25,0.25,0))
%q = zeros(2,101 * 51 * 91);
%for x = 1:101
%    for y = 1:51
%        for angle = 1:91
%            q(1, x*y*angle) = rad2deg(q1calc(-0.5 + (x-1)*0.01,0.25 + (y-1)*0.01, deg2rad(angle - 46)));
%            q(2, x*y*angle) = rad2deg(q2calc(-0.5 + (x-1)*0.01,0.25 + (y-1)*0.01, deg2rad(angle - 46)));
%        end
%    end
%end
ymin = 0.3;
box_bottom = {[-0.5, 0.5], [ymin,ymin]};
plot(box_bottom{1}, box_bottom{2}, 'b','LineWidth', 3); hold on;
box_top = {[-0.5, 0.5], [ymin + 0.5,ymin + 0.5]};
plot(box_top{1}, box_top{2}, 'b','LineWidth', 3); hold on;
box_right = {[-0.5, -0.5], [ymin,ymin + 0.5]};
plot(box_right{1}, box_right{2}, 'b','LineWidth', 3); hold on;
box_left = {[0.5, 0.5], [ymin,ymin + 0.5]};
plot(box_left{1}, box_left{2}, 'b','LineWidth', 3); hold on;

xlim([-0.75 0.75]);
ylim([-0.25 1]);

 button = 1;
 
 while sum(button) <=3   % read ginputs until a mouse right-button occurs
   [x,y,button] = ginput(1);
   disp(x)
   disp("----")
   angle = deg2rad((135-45) * rand(1) + 45);
   xpath = linspace(x - cos(angle) * 0.2, x, 100);
   ypath = linspace(y - sin(angle) * 0.2, y, 100);
   carx = [- (0.61 - 0.29) * cos(angle + pi/2) + x, 0.29 * cos(angle + pi/2) + x];
   cary = [- (0.61 - 0.29) * sin(angle + pi/2) + y, 0.29 * sin(angle + pi/2) + y];
   h2 = plot(carx, cary);
   for counter = 1:100
       if x >= 0 && angle > pi/2
            [joint1, joint2, joint3] = calculatepos(q1calcR, q2calcR, xpath(counter),ypath(counter),angle);
       elseif x >= 0 && angle <= pi/2
            [joint1, joint2, joint3] = calculatepos(q1calcL, q2calcL, xpath(counter),ypath(counter),angle);  
       elseif x < 0 && angle < pi/2
            [joint1, joint2, joint3] = calculatepos(q1calcL, q2calcL, xpath(counter),ypath(counter),angle);  
       elseif x < 0 && angle >= pi/2
            [joint1, joint2, joint3] = calculatepos(q1calcR, q2calcR, xpath(counter),ypath(counter),angle);
       end
       
       xdata = [0,joint1(1),joint2(1), joint3(1)];
       ydata = [0,joint1(2),joint2(2), joint3(2)];
       if counter == 1
           h1 = plot(xdata,ydata); hold on;
           h1.XDataSource = 'xdata';
           h1.YDataSource = 'ydata';
       else
          set(h1,'XData',xdata, 'YData',ydata);
       end
       pause(1/100)
   end
   
   counter = counter + 1;
 end

 
function [joint1, joint2, joint3] = calculatepos(q1calc, q2calc, specposx, specposy, specangle)
    l1 = 0.5;
    l2 = 0.5;
    q1 = q1calc(specposx, specposy, specangle);
    q2 = q2calc(specposx, specposy, specangle);
    joint1 = [l1 * cos(q1), l1 * sin(q1)];
    joint2 = joint1 + [l2 * cos(q1+q2), l2 * sin(q1 + q2)];
    joint3 = [specposx, specposy];
end
