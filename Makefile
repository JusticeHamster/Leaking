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
OPENCV_LIBRARY = -L$(OPENCV_HOME)/lib -lopencv_core -lopencv_imgproc -lopencv_highgui -lopencv_imgcodecs -lopencv_ml
LIBRARY := $(OPENCV_LIBRARY)
# depend
DEPEND := decolor.o

decolor : $(DEPEND)
	$(CC) $(CPPVERSION) $(LIBRARY) $(DEPEND) -o $@

decolor.o : decolor.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) decolor.cpp -o $@

.PHONY : all clean

all : decolor

clean :
	rm -rf *.o decolor