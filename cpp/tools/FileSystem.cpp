#include "FileSystem.hpp"

#include <sys/stat.h>
#include <unistd.h>

#include <fstream>

int os_mkdir(std::string path) {
  return mkdir(path.c_str(), 0777);
}

bool os_exists(std::string path) {
  return access(path.c_str(), F_OK) != -1;
}

string Loader::get(string name) {
  return m_str.get(name);
}

int Loader::get_property(string name) {
  return m_int.get(name);
}

Size Loader::get_size(string name) {
  return m_size.get(name);
}

Loader() {
}