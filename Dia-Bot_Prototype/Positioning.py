import numpy as np
import math


class Point3d:

    def __init__(self, time, x, y, z):
        self.t = time
        self.x = x
        self.y = y
        self.z = z

    def mag(self): 
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __add__(self, other):
        return Point3d(max(self.t, other.t), self.x+other.x, self.y+other.y, self.z+other.z)

    def __div__(self, other):
        return Point3d(max(self.t, other.t), self.x/other.x, self.y/other.y, self.z/other.z)

    def normalize(self):
        mag = self.mag()
        return Point3d(self.t, self.x/mag, self.y/mag, self.z/mag)
    
    def rotX(self, ang):
        c = math.cos(ang)
        s = math.sin(ang)
        m = np.array([
            [1, 0, 0,    0],
            [0, c, -1*s, 0],
            [0, s, c,    0],
            [0, 0, 0,    1]])
        v = np.array([self.x,self.y,self.z,1])
        newV = np.matmul(m,v)
        return Point3d(self.t, newV[0], newV[1], newV[2])

    def rotZ(self, ang):
        c = math.cos(ang)
        s = math.sin(ang)
        m = np.array([
            [c, -1*s, 0, 0],
            [s, c,    0, 0],
            [0, 0,    1, 0],
            [0, 0,    0, 1]])
        v = np.array([self.x,self.y,self.z,1])
        newV = np.matmul(m,v)
        return Point3d(self.t, newV[0], newV[1], newV[2])

    def multiply(self, num):
        self.x = self.x * num
        self.y = self.y * num
        self.z = self.z * num

    def __repr__(self):
        return "[t: %f, x: %f, y: %f, z: %f]" % (self.t, self.x, self.y, self.z)

# Given the current integral point and the next value to interate, return the new pooint
def getNextIntegralPoint(prev, t, int_x, int_y, int_z):
    x = prev.x + (t-prev.t)*int_x
    y = prev.y + (t-prev.t)*int_y
    z = prev.z + (t-prev.t)*int_z
    # Point3d: {time, x, y, z}
    return Point3d(t, x, y, z)

# In-place version of getNextIntegralPoint - prev is updated
def writeNextIntegralPoint(prev, t, int_x, int_y, int_z):
    x = prev.x + (t-prev.t)*int_x
    y = prev.y + (t-prev.t)*int_y
    z = prev.z + (t-prev.t)*int_z
    # Point3d: {time, x, y, z}
    prev.t = t
    prev.x = x
    prev.y = y
    prev.z = z

# Add a singular next datapoint to an integral
def addIntegralDatapoint(points, t, int_x, int_y, int_z):
    newPoint = getNextIntegralPoint(points[-1], t, int_x, int_y, int_z)
    points.append(new_pos)
    return

# Take an integral over an entire list of points
def integrate(points, t0=-1, cx=0, cy=0, cz=0, idxLo=0):
    # Initial point: time of initial raw point, '+ C' data provided in parameters defaults to zero 
    i=idxLo
    # If given an initial time, use it. If not, use the first point's time
    t = points[i].t
    if t0 != -1: 
        t = t0
    integral = [Point3d(t, cx, cy, cz)]
    while i<len(points)-1:
        addIntegralDatapoint(integral, points[i+1].t, points[i].x, points[i].y, points[i].z)
        i = i+1
    return integral

# Calibrate acceleration data to be able to rotate and remove gravity vector
# Returns filtering metrics: rotation angles in X and Z directions + gravity magnitude
def calibrateAcc(accRaw):

    # Find the first index of movement
    idx = 0
    grav = Point3d(0, 0, 0, 0)
    mags = []
    while idx < len(accRaw):#( ((abs(accRaw[idx].mag()-1) < 0.08) | 
          #   (abs(accRaw[idx+1].mag()-1) < 0.08) ) 
          #   & (accRaw[idx+1].mag() < 1.5) ): # TODO: do this better
        print(str(idx) + ":  mag = " + str(accRaw[idx].mag()))
        grav = grav + accRaw[idx]
        mags.append(accRaw[idx])
        idx = idx + 1
    print("Index beyond calibration: " + str(idx))
    print("First unused point (of mag " + str(accRaw[idx].mag()) + "): " + str(accRaw[idx]))
    # Find the average magnitude direction of gravity
    gravMag = np.mean(mags)
    grav.t = 0
    grav = grav.normalize()
    print("Average: " + str(grav))

    # Rotate data so gravity is in the -Y direction
     # First rotate about the X axis
    angX = math.acos(-1*grav.y/Point3d(0,0,grav.y,grav.z).mag())
    gravX = grav.rotX(angX)
    print("\nRotation around the X axis! Expect Z=0")
    print(f"Angle: {angX}  in degrees: {angX*180/math.pi}")
    print(f"New Point: {gravX}")

    #print("")
    
   # Then about the Z axis
    angZ = math.acos(-1*gravX.y) #/gravX.mag())
    gravZ = gravX.rotZ(-1*angZ)
    print("\nRotation around the Z axis! Expect (0, -1, 0)")
    print(f"Angle: {angZ}  in degrees: {angZ*180/math.pi}")
    print(f"New Point: {gravZ}")

    return angX, angZ, gravMag

