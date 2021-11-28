# app dir
APP_DIR = ./../..
CHAI3D_DIR = $(APP_DIR)/external/chai3d-3.2.0

# project layout
TOP_DIR = $(CHAI3D_DIR)
include $(TOP_DIR)/Makefile.common

# override bin dir
BIN_DIR = $(APP_DIR)/bin/$(OS)-$(ARCH)

# GLFW dependency
CXXFLAGS += -I$(GLFW_DIR)/include
LDFLAGS  += -L$(GLFW_DIR)/lib/$(CFG)/$(OS)-$(ARCH)-$(COMPILER)
LDLIBS   += $(LDLIBS_GLFW)

# # platform-dependent adjustments
# ifeq ($(OS), mac)
#   DEPLOY = Rez -append $(TOP_DIR)/bin/resources/icons/chai3d.rsrc -o $(OUTPUT); SetFile -a C $(OUTPUT)
# endif

# local configuration
SRC_DIR   = .
HDR_DIR   = .
OBJ_DIR   = ./obj/$(CFG)/$(OS)-$(ARCH)-$(COMPILER)
PROG      = $(notdir $(shell pwd)) 
SOURCES   = $(wildcard $(SRC_DIR)/*.cpp)
INCLUDES  = $(wildcard $(HDR_DIR)/*.h)
OBJECTS   = $(patsubst %.cpp, $(OBJ_DIR)/%.o, $(notdir $(SOURCES)))
OUTPUT    = $(BIN_DIR)/$(PROG)

all: $(OUTPUT)

$(OBJECTS): $(INCLUDES)

$(OUTPUT): $(OBJ_DIR) $(LIB_TARGET) $(OBJECTS)
	$(CXX) $(CXXFLAGS) -I$(HDR_DIR) $(OBJECTS) $(LDFLAGS) $(LDLIBS) -o $(OUTPUT)
	$(DEPLOY)

$(OBJ_DIR):
	mkdir -p $@

$(OBJ_DIR)/%.o : $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OUTPUT) $(OBJECTS) *~
	-rm -rf $(OBJ_DIR)
