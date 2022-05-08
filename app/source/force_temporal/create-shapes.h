#ifndef CREATESHAPES_H
#define CREATESHAPES_H
void createShapes(
    chai3d::cWorld*& world, 
    chai3d::cShapeBox*& base, 
    chai3d::cShapeSphere*& center,
    chai3d::cShapeSphere*& target,
    bool baseEnabled, 
    double& maxLinearForce, 
    double& maxStiffness,
    double& maxDamping,
    chai3d::cVector3d& firstTargetPosition,
    chai3d::cVector3d& centerPosition,
    chai3d::cShapeSphere*& blackHole,
    chai3d::cShapeLine*& delimiterLine1,
    chai3d::cShapeLine*& delimiterLine2,
    chai3d::cShapeLine*& delimiterLine3,
    chai3d::cShapeLine*& delimiterLine4
    );
void changeTargetPosition(
    chai3d::cShapeSphere*& target, 
    chai3d::cVector3d& firstTargetPosition,
    chai3d::cVector3d& centerPosition,
    double& angle
    );
#endif 