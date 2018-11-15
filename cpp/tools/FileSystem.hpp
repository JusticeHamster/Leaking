#pragma once

#include <string>
#include <map>
#include <exception>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

int os_mkdir(string path);
bool os_exists(string path);

class Loader {
private:
  constexpr string settings("settings.json");
  map<string, string> m_str;
  map<string, int> m_int;
  map<string, Size> m_size;
public:
  Loader();
  string get(string name);
  int get_property(string name);
  Size get_size(string name);
};

class settings_not_found_exception: public exception {
public:
  settings_not_found_exception(string message): exception(message) {}
};