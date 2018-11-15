#
# Created by RailgunHamster
# 2018.10.29
#
# 这是你本地opencv安装路径
OPENCV_HOME := /usr/local/Cellar/opencv/3.4.3

CC := g++
CPPVERSION := -std=c++1y
# include
OPENCV_INCLUDE = -I$(OPENCV_HOME)/include
INCLUDE := -I. $(OPENCV_INCLUDE)
# lib
# OPENCV_LIBRARY = -L$(OPENCV_HOME)/lib -lopencv_core -lopencv_imgproc -lopencv_highgui -lopencv_imgcodecs -lopencv_ml
OPENCV_LIBRARY = `pkg-config opencv --cflags --libs`
LIBRARY := $(OPENCV_LIBRARY)
# depend
DEPEND := main_dynamic_background.o

runnable : $(DEPEND)
	$(CC) $(CPPVERSION) $(LIBRARY) $(DEPEND) -o $@

main_dynamic_background.o : main_dynamic_background.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) main_dynamic_background.cpp -o $@

.PHONY : all clean

all : runnable

clean :
	rm -rf *.o *.jpg runnable