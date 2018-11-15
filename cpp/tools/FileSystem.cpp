#include "FileSystem.hpp"
#include "json/json.h"

#include <sys/stat.h>
#include <unistd.h>

#include <fstream>
#include <sstream>
#include <optional>
#include <memory>
#include <stdexcept>

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

  string Loader::get(string name) {
    auto& result = m[name];
    if (result.empty()) {
      check_empty_throw(name);
      result = raw[name].asString();
      m[name] = result;
    }
    return result;
  }

  int Loader::get_property(string name) {
    optional<int>& result = m_i[name];
    if (!result.has_value()) {
      check_empty_throw(name);
      result = optional<int>(raw[name].asInt());
      m_i[name] = result;
    }
    return result.value();
  }

  Size Loader::get_size(string name) {
    auto& result = m_s[name];
    if (result.empty()) {
      check_empty_throw(name);
      istringstream is(raw[name].asString());
      int l, r;
      char dot;
      is >> l >> dot >> r;
      result = Size(l, r);
      m_s[name] = result;
    }
    return result;
  }

  Loader::Loader() {
    ifstream file(settings);
    if (!file.is_open())
      throw invalid_argument(settings + string(" not found"));
    Json::CharReaderBuilder builder;
    builder["collectComments"] = false;
    Json::Value raw;
    JSONCPP_STRING errs;
    auto ok = Json::parseFromStream(builder, file, &raw, &errs);
    file.close();
    if (ok)
      this->raw = raw;
    else
      throw Json::Exception(string("Json read 《") + settings + "》 error");
  }
}