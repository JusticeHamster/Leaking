#include "FileSystem.hpp"
#include "json/json.h"

#include <sys/stat.h>
#include <unistd.h>

#include <fstream>
#include <sstream>
#include <optional>
#include <memory>
#include <stdexcept>
#include <vector>

namespace FileSystem {
  using namespace std;
  using namespace cv;

  int mkdir(std::string path) {
    return ::mkdir(path.c_str(), 0777);
  }

  bool exists(std::string path) {
    return ::access(path.c_str(), F_OK) != -1;
  }

  void Loader::check_empty_throw(string name) {
    if (raw[name].isNull())
      throw invalid_argument(name + " doesn't exist");
  }

  vector<pair<string, string>> Loader::get_videos() {
    check_empty_throw("path");
    check_empty_throw("videos");
    vector<pair<string, string>> n;
    stringstream ss;
    string name;
    const auto& path = raw["path"].asString();
    for (auto r = raw["videos"].begin(); r != raw["videos"].end(); r++) {
      const auto s = r->asString();
      ss.clear();
      ss << s;
      getline(ss, name, '.');
      n.push_back(make_pair(name, path + s));
    }
    return n;
  }

  string Loader::get_output() {
    check_empty_throw("output");
    return raw["output"].asString();
  }

  Loader::Loader() {
    ifstream file(settings);
    if (!file.is_open())
      throw invalid_argument(settings + string(" not found"));
    Json::CharReaderBuilder builder;
    builder["collectComments"] = false;
    Json::Value raw;
    JSONCPP_STRING errs;
    Json::parseFromStream(builder, file, &raw, &errs);
    this->raw = raw;
    file.close();
  }
}