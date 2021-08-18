#include<iostream>
#include<string>
#include<fstream>
//------------------------------------------------------------------------------
#include "chai3d.h"
//------------------------------------------------------------------------------
#include <GLFW/glfw3.h>
//------------------------------------------------------------------------------
using namespace chai3d;
using namespace std;

//------------------------------------------------------------------------------

//------------------------------------------------------------------------------
// GENERAL SETTINGS
//------------------------------------------------------------------------------

// stereo Mode
/*
    C_STEREO_DISABLED:            Stereo is disabled 
    C_STEREO_ACTIVE:              Active stereo for OpenGL NVDIA QUADRO cards
    C_STEREO_PASSIVE_LEFT_RIGHT:  Passive stereo where L/R images are rendered next to each other
    C_STEREO_PASSIVE_TOP_BOTTOM:  Passive stereo where L/R images are rendered above each other
*/
cStereoMode stereoMode = C_STEREO_DISABLED;

// fullscreen mode
bool fullscreen = false;

// mirrored display
bool mirroredDisplay = false;

bool lineEnabled = false;
bool baseEnabled = true;
bool attractorEnabled = true;
double maxDamping;
bool trialOngoing = false;
int trialCounter = 0;
string outputPath = "/home/Carolina/Downloads/a.csv";
//------------------------------------------------------------------------------
// DECLARED VARIABLES
//------------------------------------------------------------------------------

// a world that contains all objects of the virtual environment
cWorld* world;

// a camera to render the world in the window display
cCamera* camera;

// a light source to illuminate the objects in the world
cDirectionalLight *light;

// a haptic device handler
cHapticDeviceHandler* handler;

// a pointer to the current haptic device
cGenericHapticDevicePtr hapticDevice;

// a virtual tool representing the haptic device in the scene
cToolCursor* tool;

// a few shape primitives that compose our scene
cShapeBox* base;
cShapeBox* end_box;
cShapeBox* start_box;
cShapeLine* line;
cShapeSphere* blackHole;
double boxSize = 1.0;

// a global variable to store the position [m] of the haptic device
cVector3d hapticDevicePosition;

// a flag to indicate if the haptic simulation currently running
bool simulationRunning = false;

// a flag to indicate if the haptic simulation has terminated
bool simulationFinished = true;

// a frequency counter to measure the simulation graphic rate
cFrequencyCounter freqCounterGraphics;

// a frequency counter to measure the simulation haptic rate
cFrequencyCounter freqCounterHaptics;

// haptic thread
cThread* hapticsThread;

// a handle to window display context
GLFWwindow* window = NULL;

// current width of window
int width  = 0;

// current height of window
int height = 0;

// swap interval for the display context (vertical synchronization)
int swapInterval = 1;


//------------------------------------------------------------------------------
// DECLARED FUNCTIONS
//------------------------------------------------------------------------------

// callback when the window display is resized
void windowSizeCallback(GLFWwindow* a_window, int a_width, int a_height);

// callback when an error GLFW occurs
void errorCallback(int error, const char* a_description);

// callback when a key is pressed
void keyCallback(GLFWwindow* a_window, int a_key, int a_scancode, int a_action, int a_mods);

// this function renders the scene
void updateGraphics(void);

// this function contains the main haptics simulation loop
void updateHaptics(void);

// this function closes the application
void close(void);


//==============================================================================
/*
    DEMO:   04-shapes.cpp

    In this example we illustrate how to create some simple scene composed 
    of a few shape primitives that include the sphere, cylinder and line.

    In the haptic threads we compute the interaction between the tool (cursor)
    and the different object composing the scene. 

    A widget is also placed on the front plane to display information relative 
    to the position of the cylinder.
*/
//==============================================================================

int main(int argc, char* argv[])
{
    //--------------------------------------------------------------------------
    // INITIALIZATION
    //--------------------------------------------------------------------------

    cout << endl;
    cout << "-----------------------------------" << endl;
    cout << "CHAI3D" << endl;
    cout << "Demo: 04-shapes" << endl;
    cout << "Copyright 2003-2016" << endl;
    cout << "-----------------------------------" << endl << endl << endl;
    cout << "Keyboard Options:" << endl << endl;
    cout << "[f]    - Enable/Disable full screen mode" << endl;
    cout << "[m]    - Enable/Disable vertical mirroring" << endl;
    cout << "[q     - Exit application" << endl;
    cout << "[b/l]  - Enable/Disable base or line" << endl;
    cout << "El sujeto debe clickear antes de comenzar el test. Verde es finalizado, rojo esperando el click del sujeto y gris es trial en proceso" << endl;



    cout << endl << endl;

   
    //--------------------------------------------------------------------------
    // OPEN GL - WINDOW DISPLAY
    //--------------------------------------------------------------------------

    // initialize GLFW library
    if (!glfwInit())
    {
        cout << "failed initialization" << endl;
        cSleepMs(1000);
        return 1;
    }

    // set error callback
    glfwSetErrorCallback(errorCallback);

    // compute desired size of window
    const GLFWvidmode* mode = glfwGetVideoMode(glfwGetPrimaryMonitor());
    int w = 0.8 * mode->height;
    int h = 0.5 * mode->height;
    int x = 0.5 * (mode->width - w);
    int y = 0.5 * (mode->height - h);

    // set OpenGL version
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);

    // set active stereo mode
    if (stereoMode == C_STEREO_ACTIVE)
    {
        glfwWindowHint(GLFW_STEREO, GL_TRUE);
    }
    else
    {
        glfwWindowHint(GLFW_STEREO, GL_FALSE);
    }

    // create display context
    window = glfwCreateWindow(w, h, "CHAI3D", NULL, NULL);
    if (!window)
    {
        cout << "failed to create window" << endl;
        cSleepMs(1000);
        glfwTerminate();
        return 1;
    }

    // get width and height of window
    glfwGetWindowSize(window, &width, &height);

    // set position of window
    glfwSetWindowPos(window, x, y);

    // set key callback
    glfwSetKeyCallback(window, keyCallback);

    // set resize callback
    glfwSetWindowSizeCallback(window, windowSizeCallback);

    // set current display context
    glfwMakeContextCurrent(window);

    // sets the swap interval for the current display context
    glfwSwapInterval(swapInterval);

#ifdef GLEW_VERSION
    // initialize GLEW library
    if (glewInit() != GLEW_OK)
    {
        cout << "failed to initialize GLEW library" << endl;
        glfwTerminate();
        return 1;
    }
#endif


    //--------------------------------------------------------------------------
    // WORLD - CAMERA - LIGHTING
    //--------------------------------------------------------------------------

    // create a new world.
    world = new cWorld();

    // set the background color of the environment
    world->m_backgroundColor.setBlack();

    // create a camera and insert it into the virtual world
    camera = new cCamera(world);
    world->addChild(camera);

    // // position and orient the camera
    // camera->set( cVector3d(0.0, 0.0, 5.0),    // camera position (eye)
    //              cVector3d(0.0, 0.0, 1.0),    // lookat position (target)
    //              cVector3d(0.0, 0.0, 1.0));   // direction of the (up) vector

    // position and orient the camera
    camera->set(cVector3d(0.0, 0.0, 3.0),    // camera position (eye)
                cVector3d(0.0, 0.0, 0.0),    // lookat position (target)
                cVector3d(-1.0, 0.0, 0.0));   // direction of the (up) vector

    camera->setUseMultipassTransparency(true);

    // set the near and far clipping planes of the camera
    camera->setClippingPlanes(0.01, 10.0);

    // set stereo mode
    camera->setStereoMode(stereoMode);

    // set stereo eye separation and focal length (applies only if stereo is enabled)
    // camera->setStereoEyeSeparation(0.02);
    // camera->setStereoFocalLength(3.0);

    // set vertical mirrored display mode
    camera->setMirrorVertical(mirroredDisplay);

    // create a directional light source
    light = new cDirectionalLight(world);

    // insert light source inside world
    world->addChild(light);

    // enable light source
    light->setEnabled(true);

    // define direction of light beam
    light->setDir(-1.0, 0.0, 0.0);


    //--------------------------------------------------------------------------
    // HAPTIC DEVICES / TOOLS
    //--------------------------------------------------------------------------

    // create a haptic device handler
    handler = new cHapticDeviceHandler();

    // get access to the first available haptic device found
    handler->getDevice(hapticDevice, 0);

    // retrieve information about the current haptic device
    cHapticDeviceInfo hapticDeviceInfo = hapticDevice->getSpecifications();

    // create a tool (cursor) and insert into the world
    tool = new cToolCursor(world);
    world->addChild(tool);

    // connect the haptic device to the virtual tool
    tool->setHapticDevice(hapticDevice);

    // map the physical workspace of the haptic device to a larger virtual workspace.
    tool->setWorkspaceRadius(1.0);

    // define a radius for the virtual tool (sphere)
    tool->setRadius(0.1);
    tool->setLocalPos(0.0, 0.0, 0.0);
    
    // haptic forces are enabled only if small forces are first sent to the device;
    // this mode avoids the force spike that occurs when the application starts when 
    // the tool is located inside an object for instance. 
    // tool->setWaitForSmallForce(true);

    // start the haptic tool
    tool->start();


    //--------------------------------------------------------------------------
    // CREATING SHAPES
    //--------------------------------------------------------------------------

    ////////////////////////////////////////////////////////////////////////////
    // In the following lines create some basic shape primitives such as two
    // spheres, a line and a cylinder. For each primitive we define their
    // dimensions calling their constructor. These values can of course be 
    // modified later in the program by calling the appropriate methods 
    // (setRadius(), setHeight(), etc...). Haptic effects are also created for 
    // each object. In this example we also introduce surface and magnetic
    // effects. Settings for these effects are controlled by adjusting the 
    // different parameters in the m_material properties.
    // We suggest that you explore the different settings.
    ////////////////////////////////////////////////////////////////////////////

    // read the scale factor between the physical workspace of the haptic
    // device and the virtual workspace defined for the tool
    double workspaceScaleFactor = tool->getWorkspaceScaleFactor();

    // get properties of haptic device
    double maxStiffness	= hapticDeviceInfo.m_maxLinearStiffness / workspaceScaleFactor;
    double maxLinearForce = cMin(hapticDeviceInfo.m_maxLinearForce, 7.0);
    maxDamping   = hapticDeviceInfo.m_maxLinearDamping / workspaceScaleFactor;

    // Damping of the world
    // create some viscous environment
    cEffectViscosity* viscosity = new cEffectViscosity(world);
    world->addEffect(viscosity);
    world->m_material->setViscosity(0.5 * maxDamping);

    ////////////////////////////////////////////////////////////////////////////
    // SHAPE - BASE
    ////////////////////////////////////////////////////////////////////////////

    // create a box
    base = new cShapeBox(10.0,10.0,2.0);
    world->addChild(base);
    base -> setEnabled(baseEnabled);

    // set position
    base->setLocalPos(0.0,0.0, -1.0);
    
    // set material color
    base->m_material->setWhite();

    // create haptic effect and set properties
    base->createEffectSurface();
     
    // create magnetic effect
    base->createEffectMagnetic();
    base->m_material->setMagnetMaxDistance(10);
    base->m_material->setMagnetMaxForce(0.8 * maxLinearForce);   

    // set stiffness property
    base->m_material->setStiffness(0.5 * maxStiffness);

    ////////////////////////////////////////////////////////////////////////////
    // SHAPE - end box
    ////////////////////////////////////////////////////////////////////////////

    // create a box
    end_box = new cShapeBox(0.1,boxSize,boxSize);
    world->addChild(end_box);

    // set position
    end_box->setLocalPos(-0.5,0.0, 0.0);
    
    // set material color
    end_box->m_material->setRedDark();
    // end_box-> setUseTransparency(true);
    // end_box-> setTransparencyLevel(0.2);

    // create haptic effect and set properties
    end_box->createEffectSurface();
    
    // set stiffness property
    end_box->m_material->setStiffness(0.4 * maxStiffness);

    ////////////////////////////////////////////////////////////////////////////
    // SHAPE - start box
    ////////////////////////////////////////////////////////////////////////////

    // create a box
    start_box = new cShapeBox(0.1,0.5,0.1);
    world->addChild(start_box);

    // set position
    start_box->setLocalPos(0.8, 0.0, 0.0);

    // set material color
    start_box->m_material-> setGrayDarkSlate();
    start_box-> setUseTransparency(true);
    start_box-> setTransparencyLevel(0.2);
    start_box->createEffectSurface();
    start_box->m_material->setStiffness(0.8 * maxStiffness);

    ////////////////////////////////////////////////////////////////////////////
    // SHAPE - Attractor
    ////////////////////////////////////////////////////////////////////////////

    // create a an invisible object at the center of the world that will attract the tool
    blackHole = new cShapeSphere(0.01);
    world->addChild(blackHole);
    blackHole->setLocalPos(0.8, 0.0, 0.0);

    // create haptic effect and set properties
    blackHole->createEffectSurface();
     
    // create magnetic effect
    blackHole->createEffectMagnetic();
    blackHole->m_material->setMagnetMaxDistance(10);
    blackHole->m_material->setMagnetMaxForce(0.2 * maxLinearForce);   

    // set stiffness property
    blackHole->m_material->setStiffness(0.5 * maxStiffness);
    blackHole -> setHapticEnabled(attractorEnabled);

    ////////////////////////////////////////////////////////////////////////////
    // SHAPE - LINE
    ////////////////////////////////////////////////////////////////////////////

    // create a line
    line = new cShapeLine(start_box, end_box);
    world->addChild(line);
    line -> setEnabled(lineEnabled);
    
    
    // set color at each point
    line->m_colorPointA.setWhite();
    line->m_colorPointB.setWhite();

    // create haptic effect and set haptic properties
    line->createEffectMagnetic();
    line->m_material->setMagnetMaxDistance(0.05);
    line->m_material->setMagnetMaxForce(0.3 * maxLinearForce);

    line->m_material->setStiffness(0.2 * maxStiffness);

    //--------------------------------------------------------------------------
    // START SIMULATION
    //--------------------------------------------------------------------------

    // create a thread which starts the main haptics rendering loop
    hapticsThread = new cThread();
    hapticsThread->start(updateHaptics, CTHREAD_PRIORITY_HAPTICS);

    // setup callback when application exits
    atexit(close);


    //--------------------------------------------------------------------------
    // MAIN GRAPHIC LOOP
    //--------------------------------------------------------------------------

    // call window size callback at initialization
    windowSizeCallback(window, width, height);

    // main graphic loop
    while (!glfwWindowShouldClose(window))
    {
        // get width and height of window
        glfwGetWindowSize(window, &width, &height);

        // render graphics
        updateGraphics();

        // swap buffers
        glfwSwapBuffers(window);

        // process events
        glfwPollEvents();

        // signal frequency counter
        freqCounterGraphics.signal(1);
    }

    // close window
    glfwDestroyWindow(window);

    // terminate GLFW library
    glfwTerminate();

    // exit
    return (0);
}

//------------------------------------------------------------------------------

void windowSizeCallback(GLFWwindow* a_window, int a_width, int a_height)
{
    // update window size
    width  = a_width;
    height = a_height;

}

//------------------------------------------------------------------------------

void errorCallback(int a_error, const char* a_description)
{
    cout << "Error: " << a_description << endl;
}

//------------------------------------------------------------------------------

void keyCallback(GLFWwindow* a_window, int a_key, int a_scancode, int a_action, int a_mods)
{
    // filter calls that only include a key press
    if ((a_action != GLFW_PRESS) && (a_action != GLFW_REPEAT))
    {
        return;
    }

    // option - exit
    else if ((a_key == GLFW_KEY_ESCAPE) || (a_key == GLFW_KEY_Q))
    {
        glfwSetWindowShouldClose(a_window, GLFW_TRUE);
    }

    // option - toggle fullscreen
    else if (a_key == GLFW_KEY_F)
    {
        // toggle state variable
        fullscreen = !fullscreen;

        // get handle to monitor
        GLFWmonitor* monitor = glfwGetPrimaryMonitor();

        // get information about monitor
        const GLFWvidmode* mode = glfwGetVideoMode(monitor);

        // set fullscreen or window mode
        if (fullscreen)
        {
            glfwSetWindowMonitor(window, monitor, 0, 0, mode->width, mode->height, mode->refreshRate);
            glfwSwapInterval(swapInterval);
        }
        else
        {
            int w = 0.8 * mode->height;
            int h = 0.5 * mode->height;
            int x = 0.5 * (mode->width - w);
            int y = 0.5 * (mode->height - h);
            glfwSetWindowMonitor(window, NULL, x, y, w, h, mode->refreshRate);
            glfwSwapInterval(swapInterval);
        }
    }

    // option - toggle vertical mirroring
    else if (a_key == GLFW_KEY_M)
    {
        mirroredDisplay = !mirroredDisplay;
        camera->setMirrorVertical(mirroredDisplay);
    }

    else if (a_key == GLFW_KEY_L)
    {   
        lineEnabled = !lineEnabled;
        line -> setEnabled(lineEnabled);
    }

    else if (a_key == GLFW_KEY_B)
    {   
        baseEnabled = !baseEnabled;
        base -> setEnabled(baseEnabled);
    }

}

//------------------------------------------------------------------------------

void close(void)
{
    // stop the simulation
    simulationRunning = false;

    // wait for graphics and haptics loops to terminate
    while (!simulationFinished) { cSleepMs(100); }

    // close haptic device
    tool->stop();

    // delete resources
    delete hapticsThread;
    delete world;
    delete handler;
}

//------------------------------------------------------------------------------

void updateGraphics(void)
{
    /////////////////////////////////////////////////////////////////////
    // RENDER SCENE
    /////////////////////////////////////////////////////////////////////

    // update shadow maps (if any)
    world->updateShadowMaps(false, mirroredDisplay);

    // render world
    camera->renderView(width, height);

    // wait until all GL commands are completed
    glFinish();

    // check for any OpenGL errors
    GLenum err;
    err = glGetError();
    if (err != GL_NO_ERROR) cout << "Error:  %s\n" << gluErrorString(err);
}

//------------------------------------------------------------------------------

void updateHaptics(void)
{
    // precision clock
    cPrecisionClock clock;
    clock.reset();

    // simulation in now running
    simulationRunning  = true;
    simulationFinished = false;

    // main haptic simulation loop
    while(simulationRunning)
    {
        /////////////////////////////////////////////////////////////////////
        // SIMULATION TIME    
        /////////////////////////////////////////////////////////////////////

        // stop the simulation clock
        clock.stop();

        // read the time increment in seconds
        double timeInterval = clock.getCurrentTimeSeconds();

        // restart the simulation clock
        clock.reset();
        clock.start();

        // signal frequency counter
        freqCounterHaptics.signal(1);


        /////////////////////////////////////////////////////////////////////
        // HAPTIC FORCE COMPUTATION
        /////////////////////////////////////////////////////////////////////

        // compute global reference frames for each object
        world->computeGlobalPositions(true);

        // update position and orientation of tool
        tool->updateFromDevice();

        // compute interaction forces
        tool->computeInteractionForces();

        // send forces to haptic device
        tool->applyToDevice();

        // read user switch
        bool userSwitch = tool->getUserSwitch(0);

        /////////////////////////////////////////////////////////////////////
        // TRIAL ONGOING/FINISHED
        /////////////////////////////////////////////////////////////////////    
        
        if (userSwitch && tool->isInContact(start_box) && !trialOngoing){
            trialOngoing = true;
            trialCounter += 1;
            end_box->m_material->setGrayDim();
        }
        
        if(tool->isInContact(start_box))
        {
            attractorEnabled = !trialOngoing;
            if (!trialOngoing){end_box->m_material->setRedDark();}
            end_box -> setHapticEnabled(!attractorEnabled);
            blackHole -> setHapticEnabled(attractorEnabled);
            start_box -> setHapticEnabled(attractorEnabled);
            world->m_material->setViscosity(0.0 * maxDamping);
            
        }   

        if(tool->isInContact(end_box))
        {
            trialOngoing = false;
            attractorEnabled = !trialOngoing;
            end_box->m_material->setGreenDark();
            end_box -> setHapticEnabled(!attractorEnabled);
            blackHole -> setHapticEnabled(attractorEnabled);
            start_box -> setHapticEnabled(attractorEnabled);
            world->m_material->setViscosity(0.5 * maxDamping);
        }

        if(trialOngoing)
        {
            // read position 
            cVector3d position;
            hapticDevice->getPosition(position);
                        ofstream fout;  // Create Object of Ofstream
            ifstream fin;
            fin.open(outputPath);
            fout.open (outputPath,ios::app); // Append mode
            if(fin.is_open())
                fout<< trialCounter;
                fout<< ", ";
                fout<< position.x();
                fout<< ", ";
                fout<< position.y();
                fout<< ", ";
                fout<< position.z();
                fout<< "\n";
            // cout<<"\n Data has been appended to file";
            fin.close();
            fout.close(); // Closing the file
            

        }     

    }
    
    // exit haptics thread
    simulationFinished = true;
}

//------------------------------------------------------------------------------
