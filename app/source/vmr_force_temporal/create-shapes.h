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
    chai3d::cShapeBox*& delimiterBox1,
    chai3d::cShapeBox*& delimiterBox2,
    chai3d::cShapeBox*& delimiterBox3,
    chai3d::cShapeBox*& delimiterBox4
    );
void createDelimiterBox(
    chai3d::cWorld*& world,
    double& maxStiffness,
    chai3d::cVector3d& centerPosition,
    chai3d::cShapeBox*& delimiterBox1,
    chai3d::cShapeBox*& delimiterBox2,
    chai3d::cShapeBox*& delimiterBox3,
    chai3d::cShapeBox*& delimiterBox4,
    double angle
    );
void changeTargetPosition(
    chai3d::cShapeSphere*& target, 
    chai3d::cVector3d& firstTargetPosition,
    chai3d::cVector3d& centerPosition,
    double& angle
    );
chai3d::cVector3d rotateVectorAroundCenter(
    chai3d::cVector3d vector,
    chai3d::cVector3d centerPosition,
    double angle
    );
#endif 