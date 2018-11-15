#
# Created by RailgunHamster
# 2018.10.29
#
# 这是你本地opencv安装路径
OPENCV_HOME := /usr/local/Cellar/opencv/3.4.3
#
CC := g++
CPPVERSION := -std=c++2a
# include
OPENCV_INCLUDE = -I$(OPENCV_HOME)/include
INCLUDE := -I. -Itools/ $(OPENCV_INCLUDE)
# lib
OPENCV_LIBRARY = `pkg-config opencv --cflags --libs`
LIBRARY := $(OPENCV_LIBRARY)
# tmp
TEMP_DIR := tmp
TOOLS_DIR := tools
JSON_DIR := $(TOOLS_DIR)/json
# depend
JSON_DEPEND := $(TEMP_DIR)/json_reader.o $(TEMP_DIR)/json_writer.o $(TEMP_DIR)/json_value.o
TOOLS_DEPEND := $(TEMP_DIR)/FileSystem.o $(TEMP_DIR)/StringExtend.o $(JSON_DEPEND)
DYNAMIC_DEPEND := $(TEMP_DIR)/main_dynamic_background.o $(TOOLS_DEPEND)
STATIC_DEPEND := $(TEMP_DIR)/main_static_background.o $(TOOLS_DEPEND)

drun : dynamic
	./dynamic

srun : static
	./static

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

$(TEMP_DIR)/json_reader.o : $(JSON_DIR)/json_reader.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) $(JSON_DIR)/json_reader.cpp -o $@

$(TEMP_DIR)/json_writer.o : $(JSON_DIR)/json_writer.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) $(JSON_DIR)/json_writer.cpp -o $@

$(TEMP_DIR)/json_value.o : $(JSON_DIR)/json_value.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) $(JSON_DIR)/json_value.cpp -o $@

$(TEMP_DIR)/FileSystem.o : $(TOOLS_DIR)/FileSystem.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) $(TOOLS_DIR)/FileSystem.cpp -o $@

$(TEMP_DIR)/StringExtend.o : $(TOOLS_DIR)/StringExtend.cpp
	$(CC) -c $(CPPVERSION) $(INCLUDE) $(TOOLS_DIR)/StringExtend.cpp -o $@

.PHONY : all clean drun srun dynamic static

all : dynamic static

clean :
	rm -rf *.o tmp output dynamic static