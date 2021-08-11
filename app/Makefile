# app dir
APP_DIR = .
CHAI3D_DIR = $(APP_DIR)/external/chai3d-3.2.0

# import settings
TOP_DIR = $(CHAI3D_DIR)
include $(TOP_DIR)/Makefile.common

# override bin dir
BIN_DIR = $(APP_DIR)/bin/$(OS)-$(ARCH)

# examples
SUBDIRS  = source

# rules
all: $(SUBDIRS)

$(SUBDIRS): glfw
	$(MAKE) -C $@

glfw:
	$(MAKE) -C $(TOP_DIR)/extras/GLFW

.PHONY: $(SUBDIRS)

clean:
	@for T in $(SUBDIRS); do make -C $$T $@; done
	-rm -f core *~ *.bak #*
