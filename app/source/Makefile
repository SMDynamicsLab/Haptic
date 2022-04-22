# app dir
APP_DIR = ./..
CHAI3D_DIR = $(APP_DIR)/external/chai3d-3.2.0

# import settings
TOP_DIR = $(CHAI3D_DIR)
include $(TOP_DIR)/Makefile.common

# override bin dir
BIN_DIR = $(APP_DIR)/bin/$(OS)-$(ARCH)

# tests
SUBDIRS  = tests_previos/test1 \
           tests_previos/test2 \
           tests_previos/test3 \
		   tests_previos/test4 \
		   tests_previos/test5 \
		   tests_previos/test6 \
		   vmr \
		   vmr_temporal \
		   force \
		   force_temporal \		   



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
