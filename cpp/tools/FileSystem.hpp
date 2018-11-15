#pragma once

#include <string>

int os_mkdir(std::string path);
bool os_exists(std::string path);

class Loader {
private:
  std::string path;
public:
  Loader(std::string path): path(path) {}
};