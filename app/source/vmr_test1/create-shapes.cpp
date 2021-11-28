
#include <iostream>
#include<iostream>
#include<string>
#include<fstream>
#include "chai3d.h"
#include "create-shapes.h"
using namespace chai3d;
using namespace std;
void createShapes(
    cWorld*& world, 
    cShapeBox*& base, 
    cShapeSphere*& center,
    cShapeSphere*& target,
    bool baseEnabled, 
    double& maxLinearForce, 
    double& maxStiffness,
    double& maxDamping,
    cVector3d& firstTargetPosition,
    cVector3d& centerPostition
    )
{
    // SHAPE - BASE
    base = new cShapeBox(10.0,10.0,2.0);
    world->addChild(base);
    base-> setEnabled(baseEnabled);
    base->setLocalPos(0.0,0.0, -1.0);
    base->m_material->setWhite();
    base->createEffectSurface();
    base->createEffectMagnetic();
    base->m_material->setMagnetMaxDistance(10);
    base->m_material->setMagnetMaxForce(0.8 * maxLinearForce);   
    base->m_material->setStiffness(0.5 * maxStiffness);

    // SHAPE - target
    target = new cShapeSphere(0.10);
    world->addChild(target);
    target->setLocalPos(firstTargetPosition);
    target-> setUseTransparency(true);
    target-> setTransparencyLevel(0.8);
    target->m_material->setViscosity(0.1 * maxDamping);
    target->createEffectViscosity();
    target -> setEnabled(false);

    // SHAPE - center (start)
    center = new cShapeSphere(0.09);
    world->addChild(center);
    center->setLocalPos(centerPostition);
    center-> setUseTransparency(true);
    center-> setTransparencyLevel(0.8);
    center->m_material->setViscosity(0.1 * maxDamping);
    center->createEffectViscosity();     
}

void changeTargetPosition(
    cShapeSphere*& target,
    cVector3d& firstTargetPosition,
    cVector3d& centerPostition,
    double& angle
    )
{
    cMatrix3d rot;
    rot.identity();
    rot.rotateAboutLocalAxisDeg(0,0,1,angle);
    cVector3d new_pos = rot * (firstTargetPosition - centerPostition);
    target->setLocalPos(centerPostition + new_pos);
}