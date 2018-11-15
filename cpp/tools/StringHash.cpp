#include "StringHash.hpp"

hash_t hash_(std::string str) {
  return _hash(str.c_str());
}