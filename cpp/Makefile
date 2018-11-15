#
# Created by RailgunHamster
# 2018.10.29
#
# 这是你本地opencv安装路径
OPENCV_HOME := /usr/local/Cellar/opencv/3.4.3
#
CC := g++
CPPVERSION := -std=c++1y
# include
OPENCV_INCLUDE = -I$(OPENCV_HOME)/include
INCLUDE := -I. $(OPENCV_INCLUDE)
# lib
OPENCV_LIBRARY = `pkg-config opencv --cflags --libs`
LIBRARY := $(OPENCV_LIBRARY)
# tmp
TEMP_DIR := tmp
# depend
DYNAMIC_DEPEND := $(TEMP_DIR)/main_dynamic_background.o
STATIC_DEPEND := $(TEMP_DIR)/main_static_background.o

temp_dir :
	mkdir -p $(TEMP_DIR)

dynamic : $(DYNAMIC_DEPEND)
	$(CC) $(CPPVERSION) $(LIBRARY) $(DYNAMIC_DEPEND) -o $@

static : $(STATIC_DEPEND)
	$(CC) $(CPPVERSION) $(LIBRARY) $(STATIC_DEPEND) -o $@

$(TEMP_DIR)/main_dynamic_background.o : main_dynamic_background.cpp temp_dir
	$(CC) -c $(CPPVERSION) $(INCLUDE) main_dynamic_background.cpp -o $@

$(TEMP_DIR)/main_static_background.o : main_static_background.cpp temp_dir
	$(CC) -c $(CPPVERSION) $(INCLUDE) main_static_background.cpp -o $@

.PHONY : all clean dynamic static

all : dynamic static

clean :
	rm -rf *.o tmp output dynamic static