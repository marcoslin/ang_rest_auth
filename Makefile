#!/bin/bash

# ===========================================================
# Author:   Marcos Lin
# Created:	3 May 2013
#
# Makefile used to setup PyAngo application
#
# ===========================================================

SRC           = src
PYENV         = pyenv
PIP           = $(PYENV)/bin/pip
PYLIB_REQ     = conf/pylib_req.txt


# ------------------
# USAGE: First target called if no target specified
man :
	@cat $(SRC)/readme.make
	@cat conf/pylib_req.txt

# ------------------
# Define file needed
$(PIP) :
ifeq ($(shell which virtualenv),)
	$(error virtualenv command needed to be installed.)
endif
	@mkdir -p $(PYENV)
	@virtualenv $(PYENV)
   
$(PYENV)/pylib_req.txt : $(PYLIB_REQ)
	@$(PIP) install -r $(PYLIB_REQ)
	@cp -a $(PYLIB_REQ) $@


# ------------------
# MAIN TARGETS	
virtualenv : $(PIP) $(PYENV)/pylib_req.txt


# ------------------
# DEFINE PHONY TARGET: Basically all targets
.PHONY : \
	man virtualenv
