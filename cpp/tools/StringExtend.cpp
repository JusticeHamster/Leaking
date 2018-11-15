#include "StringExtend.hpp"

#include <sstream>

namespace StringExtend {
  using namespace std;

  hash_t hash_(std::string str) {
    return string_hash(str.c_str());
  }

  string itos(int i) {
    stringstream s;
    s << i;
    return s.str();
  }
}
