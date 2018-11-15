#include "FileSystem.hpp"

#include <sys/stat.h>
#include <unistd.h>

int os_mkdir(std::string path) {
  return mkdir(path.c_str(), 0777);
}

bool os_exists(std::string path) {
  return access(path.c_str(), F_OK) != -1;
}