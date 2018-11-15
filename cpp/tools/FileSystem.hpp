#pragma once

#include <string>
#include <map>
#include <exception>
#include <opencv2/opencv.hpp>
#include <optional>

#include "json/json.h"

namespace FileSystem {
  using namespace std;
  using namespace cv;

  int mkdir(string path);
  bool exists(string path);

  class Loader {
  private:
    static constexpr auto settings = "settings.json";
    map<string, string> m;
    map<string, optional<int>> m_i;
    map<string, Size> m_s;
    Json::Value raw;
    //
    void check_empty_throw(string name);
  public:
    Loader();
    string get(string name);
    int get_property(string name);
    Size get_size(string name);
  };
}