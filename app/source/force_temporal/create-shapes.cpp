
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
    cVector3d& centerPosition,
    cShapeSphere*& blackHole,
    cShapeLine*& delimiterLine1,
    cShapeLine*& delimiterLine2,
    cShapeLine*& delimiterLine3,
    cShapeLine*& delimiterLine4
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
    center->setLocalPos(centerPosition);
    center-> setUseTransparency(true);
    center-> setTransparencyLevel(0.8);
    center->m_material->setViscosity(0.1 * maxDamping);
    center->createEffectViscosity();

    // SHAPE - Attractor
    blackHole = new cShapeSphere(0.001);
    world->addChild(blackHole);
    blackHole->setLocalPos(firstTargetPosition);
    blackHole->createEffectSurface();
    blackHole->createEffectMagnetic();
    blackHole->m_material->setMagnetMaxDistance(10);
    blackHole->m_material->setMagnetMaxForce(0.2 * maxLinearForce);
    blackHole->m_material->setStiffness(0.5 * maxStiffness);
    blackHole -> setEnabled(false);


    // SHAPE - DELIMITER
    double x1 = 0.75;
    double y1 = 1.0;
    cVector3d arriba_izquierda = cVector3d(-x1,-y1,0);
    cVector3d arriba_derecha = cVector3d(-x1, y1,0);
    cVector3d abajo_izquierda = cVector3d(x1,-y1,0);
    cVector3d abajo_derecha = cVector3d(x1,y1,0);
    
    delimiterLine1 = new cShapeLine(arriba_izquierda, abajo_izquierda);
    delimiterLine2 = new cShapeLine(arriba_derecha, abajo_derecha);
    delimiterLine3 = new cShapeLine(arriba_izquierda, arriba_derecha);
    delimiterLine4 = new cShapeLine(abajo_izquierda, abajo_derecha);

    world->addChild(delimiterLine1);
    world->addChild(delimiterLine2);
    world->addChild(delimiterLine3);
    world->addChild(delimiterLine4);

    delimiterLine1->createEffectSurface();
    delimiterLine2->createEffectSurface();
    delimiterLine3->createEffectSurface();
    delimiterLine4->createEffectSurface();
    
    delimiterLine1->m_material->setStiffness(0.5 * maxStiffness);
    delimiterLine2->m_material->setStiffness(0.5 * maxStiffness);
    delimiterLine3->m_material->setStiffness(0.5 * maxStiffness);
    delimiterLine4->m_material->setStiffness(0.5 * maxStiffness);
    
}

void changeTargetPosition(
    cShapeSphere*& target,
    cVector3d& firstTargetPosition,
    cVector3d& centerPosition,
    double& angle
    )
{
    cMatrix3d rot;
    rot.identity();
    rot.rotateAboutLocalAxisDeg(0,0,1,angle);
    cVector3d new_pos = rot * (firstTargetPosition - centerPosition);
    target->setLocalPos(centerPosition + new_pos);
}