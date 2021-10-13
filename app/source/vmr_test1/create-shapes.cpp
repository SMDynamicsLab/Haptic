
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
    cShapeBox*& start_box,
    cShapeBox*& end_box,
    cShapeSphere*& blackHole,
    cShapeLine*& line,
    bool baseEnabled, 
    bool lineEnabled,
    bool attractorEnabled,
    double& maxLinearForce, 
    double& maxStiffness,
    double& maxDamping,
    cVector3d& firstTargetPosition,
    cVector3d& startBoxPostition
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

    // SHAPE - end box
    end_box = new cShapeBox(0.08,0.08,0.1);
    world->addChild(end_box);
    end_box->setLocalPos(firstTargetPosition);
    end_box->m_material->setRedDark();
    // end_box->createEffectSurface();
    // end_box->m_material->setStiffness(0.4 * maxStiffness);
    //     // set haptic properties
    end_box->m_material->setViscosity(0.1 * maxDamping);
    end_box->createEffectViscosity();

    // SHAPE - start box
    start_box = new cShapeBox(0.08,0.08,0.1);
    world->addChild(start_box);
    // start_box->setLocalPos(0.8, 0.0, 0.0);
    start_box->setLocalPos(startBoxPostition);
    start_box->m_material-> setGrayDarkSlate();
    start_box-> setUseTransparency(true);
    start_box-> setTransparencyLevel(0.2);
    // start_box->createEffectSurface();
    // start_box->m_material->setStiffness(0.8 * maxStiffness);
    start_box->m_material->setViscosity(0.1 * maxDamping);
    start_box->createEffectViscosity();

    // SHAPE - Attractor
    blackHole = new cShapeSphere(0.01);
    world->addChild(blackHole);
    blackHole->setLocalPos(startBoxPostition);
    blackHole->createEffectSurface();
    blackHole->createEffectMagnetic();
    blackHole->m_material->setMagnetMaxDistance(10);
    blackHole->m_material->setMagnetMaxForce(0.3 * maxLinearForce);   
    blackHole->m_material->setStiffness(0.5 * maxStiffness);
    blackHole -> setHapticEnabled(attractorEnabled);

    // SHAPE - LINE
    // line = new cShapeLine(start_box, end_box);
    line = new cShapeLine(cVector3d(0,0,0), 
                              cVector3d(0,0,0));
    world->addChild(line);
    line -> setEnabled(lineEnabled);
    line->m_colorPointA.setWhite();
    line->m_colorPointB.setRedCrimson();
    // line->createEffectMagnetic();
    // line->m_material->setMagnetMaxDistance(0.05);
    // line->m_material->setMagnetMaxForce(0.3 * maxLinearForce);
    // line->m_material->setStiffness(0.2 * maxStiffness);      
}

void changeTargetPosition(
    cShapeBox*& end_box,
    cVector3d& firstTargetPosition,
    cVector3d& startBoxPostition,
    double& angle
    )
{
    cMatrix3d rot;
    rot.identity();
    rot.rotateAboutLocalAxisDeg(0,0,1,angle);
    cVector3d new_pos = rot * (firstTargetPosition - startBoxPostition);
    end_box->setLocalPos(startBoxPostition + new_pos);
}