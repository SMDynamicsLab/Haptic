
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
    cShapeBox*& delimiterBox1,
    cShapeBox*& delimiterBox2,
    cShapeBox*& delimiterBox3,
    cShapeBox*& delimiterBox4
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

    createDelimiterBox(
        world,
        maxStiffness,
        centerPosition,
        delimiterBox1,
        delimiterBox2,
        delimiterBox3,
        delimiterBox4,
        0.0
    );
}

void createDelimiterBox(
    cWorld*& world,
    double& maxStiffness,
    cVector3d& centerPosition,
    cShapeBox*& delimiterBox1,
    cShapeBox*& delimiterBox2,
    cShapeBox*& delimiterBox3,
    cShapeBox*& delimiterBox4,
    double rotation
    )
{
    // SHAPE - DELIMITER
    double x = 0.7;
    double y = 1.0;
    double z = 1;
    world->removeChild(delimiterBox1);
    world->removeChild(delimiterBox2);
    world->removeChild(delimiterBox3);
    world->removeChild(delimiterBox4);

    delimiterBox1 = new cShapeBox(2*x, 0.05, 0.1);//izquierda
    delimiterBox2 = new cShapeBox(2*x, 0.05, 0.1);//derecha
    delimiterBox3 = new cShapeBox(0.05, 2*y, 0.1);//arriba
    delimiterBox4 = new cShapeBox(0.05, 2*y, 0.1);//abajo

    world->addChild(delimiterBox1);
    world->addChild(delimiterBox2);
    world->addChild(delimiterBox3);
    world->addChild(delimiterBox4);

    cVector3d pos1 = cVector3d(0, -y, 0);
    cVector3d pos2 = cVector3d(0, y, 0);
    cVector3d pos3 = cVector3d(-x, 0, 0);
    cVector3d pos4 = cVector3d(x, 0, 0);
    if (rotation != 0.0)
    {
        pos1 = rotateVectorAroundCenter(pos1, centerPosition, rotation);
        pos2 = rotateVectorAroundCenter(pos2, centerPosition, rotation);
        pos3 = rotateVectorAroundCenter(pos3, centerPosition, rotation);
        pos4 = rotateVectorAroundCenter(pos4, centerPosition, rotation);

        delimiterBox1 -> rotateAboutGlobalAxisDeg(0, 0, 1, rotation);
        delimiterBox2 -> rotateAboutGlobalAxisDeg(0, 0, 1, rotation);
        delimiterBox3 -> rotateAboutGlobalAxisDeg(0, 0, 1, rotation);
        delimiterBox4 -> rotateAboutGlobalAxisDeg(0, 0, 1, rotation);
    }

    delimiterBox1 -> setLocalPos(pos1);
    delimiterBox2 -> setLocalPos(pos2);
    delimiterBox3 -> setLocalPos(pos3);
    delimiterBox4 -> setLocalPos(pos4);

    delimiterBox1->createEffectSurface();
    delimiterBox2->createEffectSurface();
    delimiterBox3->createEffectSurface();
    delimiterBox4->createEffectSurface();
    
    delimiterBox1->m_material->setStiffness(0.5 * maxStiffness);
    delimiterBox2->m_material->setStiffness(0.5 * maxStiffness);
    delimiterBox3->m_material->setStiffness(0.5 * maxStiffness);
    delimiterBox4->m_material->setStiffness(0.5 * maxStiffness);
}

void changeTargetPosition(
    cShapeSphere*& target,
    cVector3d& firstTargetPosition,
    cVector3d& centerPosition,
    double& angle
    )
{
    target->setLocalPos(
        rotateVectorAroundCenter(firstTargetPosition, centerPosition, angle)
        );
}

cVector3d rotateVectorAroundCenter(
    cVector3d vector,
    cVector3d centerPosition,
    double angle
)
{
    cMatrix3d rot;
    rot.identity();
    rot.rotateAboutLocalAxisDeg(0,0,1,angle);
    cVector3d new_pos = rot * (vector - centerPosition) + centerPosition;
    return new_pos;
}