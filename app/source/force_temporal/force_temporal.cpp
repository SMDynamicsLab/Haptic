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
bool fullscreen = true; // fullscreen mode
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

    
// DECLARED MACROS
string resourceRoot; // root resource path
#define RESOURCE_PATH(p)    (char*)((resourceRoot+string(p)).c_str()) // convert to resource path

// Audio
cAudioDevice* audioDevice; // audio device to play sound
cAudioBuffer* audioBufferSuccess;
cAudioBuffer* audioBufferFailure;
cAudioBuffer* audioBufferFinished;
cAudioBuffer* audioBufferStop;
cAudioBuffer* audioBufferBeep;
cAudioBuffer* audioBufferBeepBeep1;
cAudioBuffer* audioBufferBeepBeep2;

cAudioSource* audioSourceSuccess;
cAudioSource* audioSourceFailure;
cAudioSource* audioSourceFinished;
cAudioSource* audioSourceStop;
cAudioSource* audioSourceBeep;
cAudioSource* audioSourceBeepBeep;


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
void setFullscreen(void);

// Haptic custom objects
cShapeBox* base;
cShapeSphere* target;
cShapeSphere* center;
cFontPtr font; // a font for rendering text
cFontPtr fontBig;  // a font for rendering text
cLabel* labelMessage; // a label to explain what is happening
string labelText; // text for labelMessage
cShapeSphere* blackHole; // blackhole para el descanso entre bloques

// cLabel* labelRates; // a label to display the rate [Hz] at which the simulation is running
cVector3d firstTargetPosition = cVector3d(-0.5,0.0, 0.0);
cVector3d centerPosition = cVector3d(0.5, 0.0, 0.0);

// Custom variables
bool baseEnabled = true;
double maxDamping;

time_t mod_time;
vector<double> variables;
vector<vector<double>> data;
string input;
string output;

// Camera Settings
cVector3d localPosition = cVector3d(0.0, 0.0, 2.0); // camera position (eye)
cVector3d localLookAt = cVector3d(0.0, 0.0, 0.0); // lookat position (target)
cVector3d localUp = cVector3d(-1.0, 0.0, 0.0); // direction of the (up) vector

// Trial Phases
cPrecisionClock clockTrialTime; // precision clock
cPrecisionClock clockHoldTime; // precision clock
cPrecisionClock clockWaitTime; // precision clock
bool trialOngoing = false;
bool trialSuccess;
int trialPhase = 0;
double totalTrialDurationInMs;
double totalHoldDurationInMs;
double totalWaitDurationInMs;
void startTrialPhase(int phase);
int trialCounter = 0;
int blockTrialCounter = 0;
int blockN;
int blockWaitTimeInMs = 60 * 1000;

// Camera rotation (upside down)
double cameraRotation = 0; // upside down

// Temporal variables
bool soundShouldPlay = false;
double holdBeforeSoundDurationInMs;
double holdAfterSoundDurationInMs;
double timeFirstBeep;
double timeSecondBeep;
double expectedPeriod;
string summaryOutputFile; 
vector<vector<double>> summaryData;
double maxStiffness;
void setSound(int sound);

// Feedback for temporal reproduction
cLevel* levelForFeedback; // a level widget to display feedback
cLevel* levelForReference; // a level widget to display reference
cLabel* labelFast;
cLabel* labelSlow;
void showFeedback(bool show);

// Force variables
cVector3d forceField;
bool forceEnabled = false;
cVector3d linearVelocity;
void setForceField(cVector3d position, cVector3d linearVelocity, int forceType);
double maxLinearForce;
int forceType;
cVector3d graphic_position;


// Delimiter lines
cShapeBox* delimiterBox1;
cShapeBox* delimiterBox2;
cShapeBox* delimiterBox3;
cShapeBox* delimiterBox4;

int randNum(int min, int max)
{
    int num = rand()%(max-min + 1) + min;
    return num;
}

void setVariables()
{
    // double angle = variables[0];
    forceEnabled = variables[1];

    int sound = variables[3];
    setSound(sound);

    forceType = variables[4];


    // Si el bloque dura mas de 10 trials, descansa 
    // (en la demo no descansa)
    if (blockN != variables[2]){
        if (blockTrialCounter > 10){
            trialPhase = 4;
            startTrialPhase(5); // BLOCK ENDED - wait for next trial
        }   
        blockTrialCounter = 0;
    }

    blockN = variables[2];
    // changeTargetPosition(target, firstTargetPosition, centerPosition, angle);
    
}

void setSound(int sound)
{
    switch (sound)
    {
    case 1:
        audioSourceBeepBeep = new cAudioSource();
        audioSourceBeepBeep -> setAudioBuffer(audioBufferBeepBeep1);
        audioSourceBeepBeep -> setGain(4.0);
        expectedPeriod = 444;
        break;
    case 2:
        audioSourceBeepBeep = new cAudioSource();
        audioSourceBeepBeep -> setAudioBuffer(audioBufferBeepBeep2);
        audioSourceBeepBeep -> setGain(4.0);
        expectedPeriod = 666;
        break;

    default:
        cout << "C++: Sound variable is not in options " << sound << endl;
        break;
    }
}

void addForce(cVector3d position, cVector3d linearVelocity)
{   
    // variables for forces
    graphic_position = tool->getDeviceGlobalPos(); // not in meters, in world coordinates
    setForceField(graphic_position, linearVelocity, forceType);
    tool->addDeviceGlobalForce(forceField);
}


void setForceField(cVector3d graphic_position, cVector3d linearVelocity, int forceType)
{   
    double scaleFactor;
    double Kp;
    cMatrix3d B;
    cVector3d r0;
    double theta;
    switch (forceType)
    {
    case 1: // proporcional a una comb. lin. de las componentes de v
        B = cMatrix3d(
                cVector3d(-10.1, -11.2,    0),     // col1
                cVector3d(-11.2,  11.1,    0),     // col2
                cVector3d(    0,     0,    0)      // col3
            ); // [N.sec/m]
    
        // compute linear force
        scaleFactor = (maxLinearForce) / 5;   // [N/m]
        forceField = B * linearVelocity * scaleFactor;
        break;
    case 2: // proporcional a v y F paralelo a V
        scaleFactor = (maxLinearForce) * 3; // [N/m]
        forceField = linearVelocity * scaleFactor; // > 0
        break;
    case 3: // proporcional a v  y F paralelo a -V
        scaleFactor = (maxLinearForce) * 3; // [N/m]
        forceField = - linearVelocity * scaleFactor; // < 0
        break;
    case 4: // fuerza elastica con x0 = centro y F en X
        Kp = -1.0 / (firstTargetPosition.x() - centerPosition.x()); // [N/m]
        forceField = - Kp * (graphic_position - centerPosition); // < 0 en x porque el target esta en (-0.5,0.0, 0.0)
        forceField.set(forceField.x(), 0, 0);
        scaleFactor = maxLinearForce * 0.3;   // [N/m]
        forceField = forceField * scaleFactor;
        break;
    case 5: // fuerza elastica con x0 = centro y F en -Y (izquierda)
        Kp = -1.0 / (firstTargetPosition.x() - centerPosition.x()); // [N/m]
        forceField = Kp * (graphic_position - centerPosition);
        forceField.set(0, forceField.x(), 0);
        scaleFactor = maxLinearForce * 0.3;// [N/m]
        forceField = forceField * scaleFactor;
        break;
    case 6: // matriz de rotacion a 90
        theta = 90;
        B.identity();
        B.rotateAboutLocalAxisDeg(0,0,1,theta); // [N.sec/m]
        scaleFactor = (maxLinearForce) * 3;
        forceField =  B * linearVelocity * scaleFactor;
        break;
    default:
        cout << "C++: Unknown force type: " << forceType << endl;
        forceField = cVector3d(0, 0, 0);
        break;
    }
    forceField.set(forceField.x(), forceField.y(), 0);
}

void showFeedback(bool show)
{
    levelForFeedback -> setEnabled(show);
    labelSlow -> setEnabled(show);
    labelFast -> setEnabled(show);
}

int main(int argc, char* argv[])
{
    if(argc != 3)
    {
        cout << "C++: 2 args expected " << argc-1 << " received" << endl;
        return (0); // exit
    }
    // parse first arg to try and locate resources
    resourceRoot = string(argv[0]).substr(0,string(argv[0]).find_last_of("/\\")+1);

    input = argv[1];
    output = argv[2];
    summaryOutputFile = output + "times-summary" ;
    cout << "C++: Input file is "<< input << endl;
    cout << "C++: Output file is "<< output << endl;
    cout << "C++: Summary Output file is "<< summaryOutputFile << endl;

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
    int w = 0.8 * mode -> height;
    int h = 0.5 * mode -> height;
    int x = 0.5 * (mode -> width - w);
    int y = 0.5 * (mode -> height - h);

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
    setFullscreen();

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
    world -> m_backgroundColor.setGrayLight();

    // create a camera and insert it into the virtual world
    camera = new cCamera(world);
    world -> addChild(camera);
    
    // position and orient the camera
    camera -> set(localPosition, localLookAt, localUp);

    camera -> setUseMultipassTransparency(true);

    // set the near and far clipping planes of the camera
    camera -> setClippingPlanes(0.01, 10.0);

    // set stereo mode
    camera -> setStereoMode(stereoMode);


    // set vertical mirrored display mode
    camera -> setMirrorVertical(mirroredDisplay);

    
    light = new cDirectionalLight(world); // create a directional light source
    world -> addChild(light); // insert light source inside world
    light -> setEnabled(true); // enable light source
    light -> setDir(localUp); // define direction of light beam

    //--------------------------------------------------------------------------
    // WIDGETS
    //--------------------------------------------------------------------------

    // create a font
    font = NEW_CFONTCALIBRI20();
    fontBig = NEW_CFONTCALIBRI40();
    
    // // create a label to display the haptic and graphic rate of the simulation
    // labelRates = new cLabel(font);
    // camera -> m_frontLayer -> addChild(labelRates);

    // // set font color
    // labelRates -> m_fontColor.setGrayLevel(0.4);

    // create a label with a small message
    labelMessage = new cLabel(fontBig);
    camera -> m_frontLayer -> addChild(labelMessage);

    // set font color
    labelMessage -> m_fontColor.setBlack();

    // set text message
    labelText = "";

    // update position of label
    labelMessage -> setLocalPos((int)(0.5 * (width - labelMessage -> getWidth())), 40);

    // rotate
    labelMessage -> rotateWidgetAroundCenterDeg(cameraRotation);

    // Widgets for feedback for the user
    // create a level to display velocity data
    levelForFeedback = new cLevel();
    camera->m_frontLayer->addChild(levelForFeedback);
    levelForFeedback->setLocalPos(60, 60);
    levelForFeedback->m_colorActive.setGreenDarkCyan();
    levelForFeedback->m_colorInactive.setGray();
    levelForFeedback->setRange(-50.0, 50.0);
    levelForFeedback->setWidth(40);
    levelForFeedback->setNumIncrements(46);
    levelForFeedback->setSingleIncrementDisplay(false);
    levelForFeedback->setTransparencyLevel(0.5);
    levelForFeedback->setValue(0);

    // levelForReference = new cLevel();
    levelForReference = levelForFeedback -> copy();
    camera->m_frontLayer->addChild(levelForReference);
    levelForReference->setLocalPos(20, 60);
    levelForReference->m_colorActive.setBlack();
    levelForReference->setValue(0);

    labelSlow = new cLabel(font);
    camera -> m_frontLayer -> addChild(labelSlow);
    labelSlow -> m_fontColor.setBlack();
    labelSlow -> setText("muy rápido");
    labelSlow -> setLocalPos(60 + levelForFeedback -> getWidth(), 60);

    labelFast = labelSlow -> copy();
    camera -> m_frontLayer -> addChild(labelFast);
    labelFast -> setText("muy lento");
    labelFast -> setLocalPos(60 + levelForFeedback -> getWidth(), 60 + levelForFeedback -> getHeight() - labelFast -> getHeight());

    // Rotate levels
    levelForFeedback -> rotateWidgetAroundCenterDeg(cameraRotation);
    levelForReference -> rotateWidgetAroundCenterDeg(cameraRotation);

    // Disable Feedback at first
    showFeedback(false);

    //--------------------------------------------------------------------------
    // HAPTIC DEVICES / TOOLS
    //--------------------------------------------------------------------------

    // create a haptic device handler
    handler = new cHapticDeviceHandler();

    // get access to the first available haptic device found
    handler -> getDevice(hapticDevice, 0);

    // retrieve information about the current haptic device
    cHapticDeviceInfo hapticDeviceInfo = hapticDevice -> getSpecifications();

    // create a tool (cursor) and insert into the world
    tool = new cToolCursor(world);
    world -> addChild(tool);

    // connect the haptic device to the virtual tool
    tool -> setHapticDevice(hapticDevice);

    // map the physical workspace of the haptic device to a larger virtual workspace.
    tool -> setWorkspaceRadius(1.0);

    // define a radius for the virtual tool (sphere)
    tool -> setRadius(0.07);
    tool -> setLocalPos(0.0, 0.0, 0.0);
    tool -> setDeviceGlobalPos(0.0, 0.0, 0.0);
    
    // haptic forces are enabled only if small forces are first sent to the device;
    // this mode avoids the force spike that occurs when the application starts when 
    // the tool is located inside an object for instance. 
    // tool -> setWaitForSmallForce(true);

    // start the haptic tool
    tool -> start();

    //--------------------------------------------------------------------------
    // SETUP AUDIO MATERIAL
    //--------------------------------------------------------------------------
    audioDevice = new cAudioDevice(); // create an audio device to play sounds
    camera -> attachAudioDevice(audioDevice); // attach audio device to camera
    // create audio buffers and load audio wave files
    audioBufferSuccess = new cAudioBuffer();
    bool fileload1 = audioBufferSuccess -> loadFromFile(RESOURCE_PATH("../resources/sounds/micro-bell.wav"));

    audioBufferFailure = new cAudioBuffer();
    bool fileload2 = audioBufferFailure -> loadFromFile(RESOURCE_PATH("../resources/sounds/cartoon-bing-low.wav"));

    audioBufferFinished = new cAudioBuffer();
    bool fileload3 = audioBufferFinished -> loadFromFile(RESOURCE_PATH("../resources/sounds/tada.wav"));

    audioBufferStop = new cAudioBuffer();
    bool fileload4 = audioBufferStop -> loadFromFile(RESOURCE_PATH("../resources/sounds/stop.wav"));

    audioBufferBeep = new cAudioBuffer();
    bool fileload5 = audioBufferBeep -> loadFromFile(RESOURCE_PATH("../resources/sounds/beep_30.wav"));

    audioBufferBeepBeep1 = new cAudioBuffer();
    bool fileload6 = audioBufferBeepBeep1 -> loadFromFile(RESOURCE_PATH("../resources/sounds/beep_beep_444.wav"));

    audioBufferBeepBeep2 = new cAudioBuffer();
    bool fileload7 = audioBufferBeepBeep2 -> loadFromFile(RESOURCE_PATH("../resources/sounds/beep_beep_666.wav"));


    // check for errors
    if (!(fileload1 && fileload2 && fileload3 && fileload4 && fileload5 && fileload6 && fileload7))
    {
        cout << "Error - Sound file failed to load or initialize correctly." << endl;
        close();
        return (-1);
    }

    audioSourceSuccess = new cAudioSource();
    audioSourceSuccess -> setAudioBuffer(audioBufferSuccess);
    audioSourceSuccess -> setGain(4.0);

    audioSourceFailure = new cAudioSource();
    audioSourceFailure -> setAudioBuffer(audioBufferFailure);
    audioSourceFailure -> setGain(4.0);

    audioSourceFinished = new cAudioSource();
    audioSourceFinished -> setAudioBuffer(audioBufferFinished);
    audioSourceFinished -> setGain(4.0);

    audioSourceStop = new cAudioSource();
    audioSourceStop -> setAudioBuffer(audioBufferStop);
    audioSourceStop -> setGain(4.0);

    audioSourceBeep = new cAudioSource();
    audioSourceBeep -> setAudioBuffer(audioBufferBeep);
    audioSourceBeep -> setGain(4.0);

    //--------------------------------------------------------------------------
    // CREATE OBJECTS / SET WORLD PROPERTIES
    //--------------------------------------------------------------------------

    // read the scale factor between the physical workspace of the haptic
    // device and the virtual workspace defined for the tool
    double workspaceScaleFactor = tool -> getWorkspaceScaleFactor();
    
    // get properties of haptic device
    maxStiffness	= hapticDeviceInfo.m_maxLinearStiffness / workspaceScaleFactor;
    maxLinearForce = cMin(hapticDeviceInfo.m_maxLinearForce, 7.0);
    cout << "hapticDeviceInfo.m_maxLinearForce" << hapticDeviceInfo.m_maxLinearForce << endl;
    maxDamping   = hapticDeviceInfo.m_maxLinearDamping / workspaceScaleFactor;

    // Damping of the world
    // create some viscous environment
    cEffectViscosity* viscosity = new cEffectViscosity(world);
    world -> addEffect(viscosity);

    world -> m_material -> setViscosity(0.5 * maxDamping);
    createShapes(
        world, 
        base, 
        center,
        target,
        baseEnabled, 
        maxLinearForce, 
        maxStiffness,
        maxDamping,
        firstTargetPosition,
        centerPosition,
        blackHole,
        delimiterBox1,
        delimiterBox2,
        delimiterBox3,
        delimiterBox4
        );
   

    //--------------------------------------------------------------------------
    // START SIMULATION
    //--------------------------------------------------------------------------

    // create a thread which starts the main haptics rendering loop
    hapticsThread = new cThread();
    hapticsThread -> start(updateHaptics, CTHREAD_PRIORITY_HAPTICS);

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

}

//------------------------------------------------------------------------------

void errorCallback(int a_error, const char* a_description)
{
    cout << "C++: Error: " << a_description << endl;
}

//------------------------------------------------------------------------------
void setFullscreen()
{
    // get handle to monitor
    GLFWmonitor* monitor = glfwGetPrimaryMonitor();

    // get information about monitor
    const GLFWvidmode* mode = glfwGetVideoMode(monitor);

    // set fullscreen or window mode
    if (fullscreen)
    {
        glfwSetWindowMonitor(window, monitor, 0, 0, mode -> width, mode -> height, mode -> refreshRate);
        glfwSwapInterval(swapInterval);
    }
    else
    {
        int w = 0.8 * mode -> height;
        int h = 0.5 * mode -> height;
        int x = 0.5 * (mode -> width - w);
        int y = 0.5 * (mode -> height - h);
        glfwSetWindowMonitor(window, NULL, x, y, w, h, mode -> refreshRate);
        glfwSwapInterval(swapInterval);
    }

}

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
        setFullscreen();
    }

    // option - toggle vertical mirroring
    else if (a_key == GLFW_KEY_M)
    {
        mirroredDisplay = !mirroredDisplay;
        camera -> setMirrorVertical(mirroredDisplay);
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
    tool -> stop();

    // delete resources
    delete hapticsThread;
    delete world;
    delete handler;
    delete audioDevice;

    delete audioBufferSuccess;
    delete audioBufferFailure;
    delete audioBufferFinished;
    delete audioBufferStop;

    delete audioSourceSuccess;
    delete audioSourceFailure;
    delete audioSourceFinished;
    delete audioSourceStop;

}

//------------------------------------------------------------------------------

void updateGraphics(void)
{
    /////////////////////////////////////////////////////////////////////
    // UPDATE WIDGETS
    /////////////////////////////////////////////////////////////////////

    // // update haptic and graphic rate data
    // labelRates -> setText(cStr(freqCounterGraphics.getFrequency(), 0) + " Hz / " +
    //                     cStr(freqCounterHaptics.getFrequency(), 0) + " Hz");

    // // update position of label
    // labelRates -> setLocalPos((int)(0.5 * (width - labelRates -> getWidth())), 15);

    // set text for labelMessage
    labelMessage -> setText(labelText);

    // rotate
    labelMessage -> rotateWidgetAroundCenterDeg(cameraRotation);  
    // update position of label
    labelMessage -> setLocalPos((int)(0.5 * (width - labelMessage -> getWidth())), 40);
    // rotate
    labelMessage -> rotateWidgetAroundCenterDeg(cameraRotation);


    /////////////////////////////////////////////////////////////////////
    // RENDER SCENE
    /////////////////////////////////////////////////////////////////////

    // update shadow maps (if any)
    world -> updateShadowMaps(false, mirroredDisplay);

    // render world
    camera -> renderView(width, height);

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
    clockTrialTime.reset();
    clockHoldTime.reset();
    clockWaitTime.reset();

    // simulation in now running
    simulationRunning  = true;
    simulationFinished = false;

    startTrialPhase(trialPhase);

    vector<double> row;
    cVector3d position;
    double timeSinceHoldStartedInMs;
    double timeSinceTrialStartedInMs;
    double timeSinceWaitStartedInMs;

    double centerDistance;
    double targetDistance;
    cVector3d toolGlobalPosXY;

    // main haptic simulation loop
    while(simulationRunning)
    {   
        /////////////////////////////////////////////////////////////////////
        // SIMULATION TIME    
        /////////////////////////////////////////////////////////////////////
        freqCounterHaptics.signal(1); // signal frequency counter    

        // HAPTIC FORCE COMPUTATION
        world -> computeGlobalPositions(true); // compute global reference frames for each object
        tool -> updateFromDevice(); // update position and orientation of tool
        tool -> computeInteractionForces(); // compute interaction forces
                    
        hapticDevice->getPosition(position); // read position [m]
        hapticDevice->getLinearVelocity(linearVelocity); // read linear velocity [m/s]

        if (trialOngoing && forceEnabled)
        {
            addForce(position, linearVelocity);
        }
        
        tool -> applyToDevice(); // send forces to haptic device
        
        if (trialOngoing)
        {
            // read position
            // hapticDevice -> getPosition(position); //[m]

            // read the clockTrialTime increment in seconds
            timeSinceTrialStartedInMs = clockTrialTime.stop() * 1000; 
            clockTrialTime.start();

            //save position
            row = {timeSinceTrialStartedInMs, position.x(), position.y(), position.z(), forceField.x(), forceField.y(), forceField.z()}; // aca agregar el tiempo {t, x, y , z}
            data.push_back(row);
        }

        //Calculate distances
        toolGlobalPosXY = tool -> getDeviceGlobalPos();
        toolGlobalPosXY = cVector3d(toolGlobalPosXY.x(), toolGlobalPosXY.y(), 0);
        centerDistance = (toolGlobalPosXY).distance(center -> getGlobalPos());
        targetDistance = (toolGlobalPosXY).distance(target -> getGlobalPos());
        
        switch(trialPhase) 
        {   
            case 0: // GO TO CENTER
                // Si esta en el centro:
                if(centerDistance < 0.03)
                {
                    trialPhase = 1;
                    startTrialPhase(trialPhase); // HOLD CENTER
                }
            break;
            case 1: // HOLD CENTER
                // read the clockHoldTime increment in seconds
                timeSinceHoldStartedInMs = clockHoldTime.stop() * 1000; 
                clockHoldTime.start();

                // Si se salió del centro:
                if (centerDistance > 0.03) // Moved outside of center
                {   
                    trialPhase = 0;
                    startTrialPhase(trialPhase); // GO TO CENTER
                    
                }

                // Si tiene que hacer el sonido:
                else if (soundShouldPlay)
                {
                    // Si ya paso el tiempo antes de reproducir el sonido:
                    if (timeSinceHoldStartedInMs > holdBeforeSoundDurationInMs)
                    {
                        audioSourceBeepBeep -> play();
                        soundShouldPlay = false;
                    }
                }

                // Si ya estuvo el tiempo suficiente: (total = before + after)
                else if (timeSinceHoldStartedInMs > totalHoldDurationInMs) //center hold finished
                {   
                    trialPhase = 2;
                    data.clear();
                    clockTrialTime.reset(); // restart the clock
                    trialOngoing = true;
                    startTrialPhase(trialPhase); // TRIAL ONGOING
                }   
            break;
            case 2: // TRIAL ONGOING 
                // Si salió del centro:
                // if (centerDistance > 0.03) //Tool is outside center
                if (timeFirstBeep == 0 && ! tool -> isInContact(center)) //Tool is not in contact with center
                {   
                    timeFirstBeep = timeSinceTrialStartedInMs;
                    audioSourceBeep -> play();
                }
                // Si entró al target:
                // else if (targetDistance < 0.03) //Tool is inside target
                else if (tool -> isInContact(target)) //Tool is in contact with target
                {
                    timeSecondBeep = timeSinceTrialStartedInMs;
                    audioSourceBeep -> play();
                    trialSuccess = true;
                    trialPhase = 3;
                    clockHoldTime.reset(); // restart the clock
                    startTrialPhase(trialPhase); // HOLD TARGET
                }
                // Si se le acabó el tiempo:
                else if ((timeSinceTrialStartedInMs - timeFirstBeep) > totalTrialDurationInMs)
                {   
                    trialSuccess = false;
                    audioSourceFailure -> play();
                    labelText = "Se acabó el tiempo, intenta de nuevo";
                    trialPhase = 4;
                    startTrialPhase(trialPhase); // GO TO CENTER
                    
                }
                else if (tool -> isInContact(delimiterBox1) ||tool -> isInContact(delimiterBox2) ||tool -> isInContact(delimiterBox3) ||tool -> isInContact(delimiterBox4))
                {   
                    labelText = "Fuera de zona, intenta de nuevo";
                    trialSuccess = false;
                    audioSourceFailure -> play();
                    trialPhase = 4;
                    startTrialPhase(trialPhase); // GO TO CENTER
                }

            break;
            case 3:  // HOLD TARGET
                // read the clockHoldTime increment in seconds
                timeSinceHoldStartedInMs = clockHoldTime.stop() * 1000; 
                clockHoldTime.start();

                // POR AHORA no pasa nada si no mantiene
                // // Si salió del centro: 
                // if (targetDistance > 0.03) //Moved outside of target
                // {
                //     trialPhase = 3;  
                //     startTrialPhase(trialPhase); // Trial is still ongoing
                // }

                // Si ya mantuvo suficiente tiempo el target:
                // else if 
                if (timeSinceHoldStartedInMs > totalHoldDurationInMs) //Target hold finished
                {   
                    // audioSourceSuccess -> play();
                    trialPhase = 4;
                    startTrialPhase(trialPhase); // TRIAL ENDED - wait for next trial
                }
            break;
            case 4: // TRIAL ENDED - wait for next trial 
                // read the clockWaitTime increment in seconds
                timeSinceWaitStartedInMs = clockWaitTime.stop() * 1000; 
                clockWaitTime.start();

                // Si ya pasó el tiempo de espera:
                if (timeSinceWaitStartedInMs > totalWaitDurationInMs) // TRIAL SUCCESFUL / WAITING FOR NEXT TRIAL
                {
                    trialPhase = 0;
                    startTrialPhase(trialPhase);
                }
            break;
            case 6: // END SIMULATION 
                // read the clockWaitTime increment in seconds
                timeSinceWaitStartedInMs = clockWaitTime.stop() * 1000; 
                clockWaitTime.start();
                // Si ya pasó el tiempo de espera:
                if (timeSinceWaitStartedInMs > totalWaitDurationInMs) // TRIAL SUCCESFUL / WAITING FOR NEXT TRIAL
                {
                    glfwSetWindowShouldClose(window, GLFW_TRUE);
                }
            break;
            default:
                cout << "C++: Invalid phase" << trialPhase << endl;  
        }
    }
    
    // exit haptics thread
    simulationFinished = true;
}


void startTrialPhase(int phase)
{   
    // clockPhaseTime.reset(); // restart the clock
    bool trialShouldStart;
    blackHole -> setEnabled(false);
    switch(phase) 
    {   
        case 0: // GO TO CENTER
            data.clear();
            center -> m_material -> setBlueAqua();
            tool -> setShowEnabled(true);
            center -> setEnabled(true);
            target -> setEnabled(false);

            labelText = "Ir al inicio";
            break;
        case 1: // HOLD CENTER
            showFeedback(false);
            clockHoldTime.reset(); // restart the clock
            center -> m_material -> setGreenDark();


            trialShouldStart = getVariables(input, mod_time, variables); // input file ya no existe (la simulacion termino)

            if (!trialShouldStart)
            {   
                trialPhase = 6; // END SIMULATION 
                startTrialPhase(trialPhase);
                break;
            }

            soundShouldPlay = true ;
            holdBeforeSoundDurationInMs = randNum(1000, 2000); //randNum(500, 1000);
            holdAfterSoundDurationInMs = randNum(1000, 2000); //randNum(500, 1000);
            totalHoldDurationInMs = holdBeforeSoundDurationInMs + holdAfterSoundDurationInMs;
            labelText = "Mantener";
            setVariables();
            timeFirstBeep = 0;
            timeSecondBeep = 0;
            break;
        case 2: // TRIAL ONGOING
            center -> setEnabled(true);
            target -> setEnabled(true);
            target -> m_material -> setRedDark();

            totalTrialDurationInMs = 2000; 
            labelText = "Reproducir sonido escuchado";
            break;
        case 3: // HOLD TARGET AFTER TRIAL
            forceEnabled = false;
            center -> setEnabled(false);
            target -> m_material -> setGreenDark();
            totalHoldDurationInMs = 500;
            labelText = "Mantener";
            break;
        case 4: // TRIAL ENDED - wait for next trial
            forceEnabled = false;
            clockWaitTime.reset(); // restart the clock

            trialOngoing = false;
            target -> setEnabled(false);
            tool -> setShowEnabled(false);
            
            // Save data
            appendToCsv(output, data, trialCounter, variables, trialSuccess);
            data.clear();

            // Save summary data
            summaryData.push_back({timeFirstBeep, timeSecondBeep, expectedPeriod}); // aca agrega el tiempo inicial y final
            appendToCsv(summaryOutputFile, summaryData, trialCounter, variables, trialSuccess);
            summaryData.clear();

            trialCounter += 1;
            blockTrialCounter += 1;
            
            totalWaitDurationInMs = randNum(1000, 2000); //randNum(500, 1500); // deberia ser random entre 500 y 1.5s

            if (trialSuccess)
            {   
                double reproducedPeriod = timeSecondBeep - timeFirstBeep ;
                int percentMiss = round((reproducedPeriod - expectedPeriod) / expectedPeriod * 100);
                levelForFeedback->setValue(percentMiss); // rapido es un valor < 0
                showFeedback(true);
                labelText = "";
            }

            break;
        case 5: // BLOCK ENDED - wait some time 
            clockWaitTime.reset(); // restart the clock
            trialOngoing = false;
            center -> setEnabled(false);
            target -> setEnabled(false);
            tool -> setShowEnabled(false);
            totalWaitDurationInMs = blockWaitTimeInMs; // 1 minuto
            labelText = "Tomar un descanso.";
            audioSourceStop -> play();
            blackHole -> setEnabled(true);
            break;
        case 6: // END SIMULATION 
            clockWaitTime.reset();
            totalWaitDurationInMs = 10000; // 10s
            cout << "C++: no more trials" << endl;
            tool -> setShowEnabled(false);
            center -> setEnabled(false);
            target -> setEnabled(false);
            labelText = "Experimento terminado. Gracias!";
            audioSourceFinished -> play();
        break;
        default:
            cout << "C++: Invalid phase " << phase << endl;  
    }
}




