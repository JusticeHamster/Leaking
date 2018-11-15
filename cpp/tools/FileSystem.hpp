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
    Json::Value raw;
    //
    void check_empty_throw(string name);
  public:
    Loader();
    map<string, string> get_videos();
    string get_output();
    double get(string name);
  };
}