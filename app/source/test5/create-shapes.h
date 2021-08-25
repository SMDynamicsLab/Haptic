#ifndef CREATESHAPES_H
#define CREATESHAPES_H
void createShapes(
    chai3d::cWorld*& world, 
    chai3d::cShapeBox*& base, 
    chai3d::cShapeBox*& start_box,
    chai3d::cShapeBox*& end_box,
    chai3d::cShapeSphere*& blackHole,
    chai3d::cShapeLine*& line,
    bool baseEnabled, 
    bool lineEnabled, 
    bool attractorEnabled,
    double& maxLinearForce, 
    double& maxStiffness
    );
#endif 