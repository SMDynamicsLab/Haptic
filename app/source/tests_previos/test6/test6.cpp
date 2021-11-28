#include<iostream>
#include<string>
#include<fstream>

// #include <unistd.h> //for sleep();
#include <sys/types.h>
#include <sys/stat.h>

#include "chai3d.h"
#include <GLFW/glfw3.h>
#include "create-shapes.h"
#include "parser.h"

using namespace chai3d;
using namespace std;
//------------------------------------------------------------------------------
// stereo Mode
/*
    C_STEREO_DISABLED:            Stereo is disabled 
    C_STEREO_ACTIVE:              Active stereo for OpenGL NVDIA QUADRO cards
    C_STEREO_PASSIVE_LEFT_RIGHT:  Passive stereo where L/R images are rendered next to each other
    C_STEREO_PASSIVE_TOP_BOTTOM:  Passive stereo where L/R images are rendered above each other
*/

// General settings
cStereoMode stereoMode = C_STEREO_DISABLED;
bool fullscreen = false; // fullscreen mode
bool mirroredDisplay = false; // mirrored display
cVector3d hapticDevicePosition; // a global variable to store the position [m] of the haptic device
bool simulationRunning = false; // a flag to indicate if the haptic simulation currently running
bool simulationFinished = true; // a flag to indicate if the haptic simulation has terminated
cFrequencyCounter freqCounterGraphics; // a frequency counter to measure the simulation graphic rate
cFrequencyCounter freqCounterHaptics; // a frequency counter to measure the simulation haptic rate
cThread* hapticsThread; // haptic thread
GLFWwindow* window = NULL; // a handle to window display context
int width  = 0; // current width of window
int height = 0; // current height of window
int swapInterval = 1; // swap interval for the display context (vertical synchronization)

// Haptic Basics
cWorld* world; // a world that contains all objects of the virtual environment
cCamera* camera; // a camera to render the world in the window display
cDirectionalLight *light; // a light source to illuminate the objects in the world
cHapticDeviceHandler* handler; // a haptic device handler
cGenericHapticDevicePtr hapticDevice; // a pointer to the current haptic device
cToolCursor* tool; // a virtual tool representing the haptic device in the scene

// DECLARED FUNCTIONS
void windowSizeCallback(GLFWwindow* a_window, int a_width, int a_height); // callback when the window display is resized
void errorCallback(int error, const char* a_description); // callback when an error GLFW occurs
void keyCallback(GLFWwindow* a_window, int a_key, int a_scancode, int a_action, int a_mods); // callback when a key is pressed
void updateGraphics(void); // this function renders the scene
void updateHaptics(void); // this function contains the main haptics simulation loop
void close(void); // this function closes the application

// Haptic custom objects
cShapeBox* base;
cShapeBox* end_box;
cShapeBox* start_box;
cShapeLine* line;
cShapeSphere* blackHole;
cFontPtr font; // a font for rendering text
cLabel* labelMessage; // a label to explain what is happening
cLabel* labelRates; // a label to display the rate [Hz] at which the simulation is running
cVector3d firstTargetPosition = cVector3d(-0.5,0.0, 0.0);
cVector3d startBoxPostition = cVector3d(0.0, 0.0, 0.0);

// Custom variables
bool lineEnabled = false;
bool baseEnabled = true;
bool attractorEnabled = true;
double maxDamping;
bool trialOngoing = false;
int trialCounter = 0;
string outputPath = "/home/Carolina/Downloads/a.csv";
bool useDamping = false; // a flag for using damping (ON/OFF)
bool useForceField = true; // a flag for using force field (ON/OFF)
bool cursorVisible = true;

time_t mod_time;
vector<double> variables;
vector<vector<double>> data;
string input;
string output;

void setVariables()
{
    double angle = variables[0];
    cursorVisible = variables[1];
    useForceField = variables[2];
    changeTargetPosition(end_box, firstTargetPosition, startBoxPostition, angle);
    tool -> setShowEnabled(cursorVisible);
}

int main(int argc, char* argv[])
{
    if(argc != 3)
    {
        cout << "2 args expected " << argc-1 << " received" << endl;
        return (0); // exit
    }
    input = argv[1];
    output = argv[2];
    cout << "Input file is "<< input << endl;
    cout << "Output file is "<< output << endl;

    // OPEN GL - WINDOW DISPLAY
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

    glfwGetWindowSize(window, &width, &height); // get width and height of window
    glfwSetWindowPos(window, x, y); // set position of window
    glfwSetKeyCallback(window, keyCallback); // set key callback
    glfwSetWindowSizeCallback(window, windowSizeCallback); // set resize callback
    glfwMakeContextCurrent(window); // set current display context
    glfwSwapInterval(swapInterval); // sets the swap interval for the current display context

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
    
    // position and orient the camera
    camera->set(cVector3d(0.0, 0.0, 2.0),    // camera position (eye)
                cVector3d(0.0, 0.0, 0.0),    // lookat position (target)
                cVector3d(-1.0, 0.0, 0.0));   // direction of the (up) vector

    camera->setUseMultipassTransparency(true);

    // set the near and far clipping planes of the camera
    camera->setClippingPlanes(0.01, 10.0);

    // set stereo mode
    camera->setStereoMode(stereoMode);


    // set vertical mirrored display mode
    camera->setMirrorVertical(mirroredDisplay);

    
    light = new cDirectionalLight(world); // create a directional light source
    world->addChild(light); // insert light source inside world
    light->setEnabled(true); // enable light source
    light->setDir(-1.0, 0.0, 0.0); // define direction of light beam



    //--------------------------------------------------------------------------
    // WIDGETS
    //--------------------------------------------------------------------------

    // create a font
    font = NEW_CFONTCALIBRI20();
    
    // create a label to display the haptic and graphic rate of the simulation
    labelRates = new cLabel(font);
    camera->m_frontLayer->addChild(labelRates);

    // set font color
    labelRates->m_fontColor.setGrayLevel(0.4);

    // create a label with a small message
    labelMessage = new cLabel(font);
    camera->m_frontLayer->addChild(labelMessage);

    // set font color
    labelMessage->m_fontColor.setBlack();

    // set text message
    labelMessage->setText("Test output message");


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
    tool->setRadius(0.02);
    tool->setLocalPos(0.0, 0.0, 0.0);
    tool->setDeviceGlobalPos(0.0, 0.0, 0.0);
    
    // haptic forces are enabled only if small forces are first sent to the device;
    // this mode avoids the force spike that occurs when the application starts when 
    // the tool is located inside an object for instance. 
    // tool->setWaitForSmallForce(true);

    // start the haptic tool
    tool->start();
    tool -> setShowEnabled(cursorVisible);

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
    createShapes(
        world, 
        base, 
        start_box,
        end_box,
        blackHole,
        line,
        baseEnabled, 
        lineEnabled,
        attractorEnabled,
        maxLinearForce, 
        maxStiffness,
        maxDamping,
        firstTargetPosition,
        startBoxPostition
        );

    

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

// ------------------------------------------------------------------------------

void windowSizeCallback(GLFWwindow* a_window, int a_width, int a_height)
{
    // update window size
    width  = a_width;
    height = a_height;

    // update position of label
    labelMessage->setLocalPos((int)(0.5 * (width - labelMessage->getWidth())), 40);

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

    // option - enable/disable force field
    else if (a_key == GLFW_KEY_1)
    {
        useForceField = !useForceField;
        if (useForceField)
            cout << "> Enable force field     \r";
        else
            cout << "> Disable force field    \r";
    }

    // option - enable/disable damping
    else if (a_key == GLFW_KEY_2)
    {
        useDamping = !useDamping;
        if (useDamping)
            cout << "> Enable damping         \r";
        else
            cout << "> Disable damping        \r";
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
    // UPDATE WIDGETS
    /////////////////////////////////////////////////////////////////////

    // update haptic and graphic rate data
    labelRates->setText(cStr(freqCounterGraphics.getFrequency(), 0) + " Hz / " +
                        cStr(freqCounterHaptics.getFrequency(), 0) + " Hz");

    // update position of label
    labelRates->setLocalPos((int)(0.5 * (width - labelRates->getWidth())), 15);


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
        clock.stop(); // stop the simulation clock
        double timeInterval = clock.getCurrentTimeSeconds(); // read the time increment in seconds
        clock.reset(); // restart the simulation clock
        clock.start(); 
        freqCounterHaptics.signal(1); // signal frequency counter


        

        // PARSE FILE IF MODIFIED

    

        // HAPTIC FORCE COMPUTATION
        world->computeGlobalPositions(true); // compute global reference frames for each object
        tool->updateFromDevice(); // update position and orientation of tool
        tool->computeInteractionForces(); // compute interaction forces
        // tool->applyToDevice(); // send forces to haptic device
        
        // TRIAL ONGOING/FINISHED
        bool trialFinishedManually=false;
        bool userSwitch = tool->getUserSwitch(0); // read user switch
        if (userSwitch && tool->isInContact(start_box) && !trialOngoing){
            trialOngoing = true;
            end_box->m_material->setGrayDim();
            getVariables(input, mod_time, variables);
            setVariables();
            
        }
        else if (userSwitch && (tool->getDeviceGlobalPos()).distance(startBoxPostition) > 0.1) 
        {
            trialFinishedManually = true;
        }
        

        if(tool->isInContact(start_box))
        {
            attractorEnabled = !trialOngoing;
            if (!trialOngoing){end_box->m_material->setRedDark();}
            end_box -> setEnabled(!attractorEnabled);
            blackHole -> setHapticEnabled(attractorEnabled);
            start_box -> setHapticEnabled(attractorEnabled);
            world->m_material->setViscosity(0.0 * maxDamping);
            
        }   
        


        if(tool->isInContact(end_box) or trialFinishedManually)
        {
            if (trialOngoing){
                trialOngoing = false;
                appendToCsv(output, data, trialCounter, variables);
                data.clear();
                trialCounter += 1;
            }



            attractorEnabled = !trialOngoing;
            end_box->m_material->setGreenDark();
            end_box -> setEnabled(!attractorEnabled);

            blackHole -> setHapticEnabled(attractorEnabled);
            start_box -> setHapticEnabled(attractorEnabled);
            world->m_material->setViscosity(0.5 * maxDamping);
        }
        
        if(trialOngoing)
        {    
            /////////////////////////////////////////////////////////////////////
            // READ HAPTIC DEVICE
            /////////////////////////////////////////////////////////////////////
            // read position
            cVector3d position;
            hapticDevice->getPosition(position);

            // read linear velocity 
            cVector3d linearVelocity;
            hapticDevice->getLinearVelocity(linearVelocity); //[m/s]

            //save position
            vector<double> row = {position.x(), position.y(), position.z()};
            data.push_back(row);
            
            


            /////////////////////////////////////////////////////////////////////
            // COMPUTE AND APPLY FORCES
            /////////////////////////////////////////////////////////////////////
      
            // apply force field
            if (useForceField)
            {   
                // variables for forces
                cVector3d force (0,0,0);  

                cMatrix3d B = cMatrix3d(
                    cVector3d(-10.1, -11.2,    0),     // col1
                    cVector3d(-11.2,  11.1,    0),     // col2
                    cVector3d(    0,     0,    0)      // col3
                ); // [N.sec/m]

                // compute linear force
                cVector3d forceField = B * linearVelocity * 0.5;
                force.add(forceField);
                labelMessage->setText("force" + force.str());
                tool->addDeviceGlobalForce(force);
                
                // cout << "position" << position << endl;
                // cout << "linearVelocity" << linearVelocity << endl;
                // cout << "force" << force  << endl;
                if (lineEnabled){
                    // update arrow
                    line->m_pointB = force;
                    cout << "line->m_pointA" << line->m_pointA << endl;
                    cout << "line->m_pointB" << line->m_pointB << endl;
                    cout << "position" << position << endl;
                }
            }
            

            
        }
        tool->applyToDevice(); // send forces to haptic device        
        // cout << "tool->getDeviceGlobalForce()" << tool->getDeviceGlobalForce() << endl;

    }
    
    // exit haptics thread
    simulationFinished = true;
}

