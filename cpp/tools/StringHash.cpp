#include "StringHash.hpp"

namespace StringHash {
  hash_t hash_(std::string str) {
    return string_hash(str.c_str());
  }
}