#pragma once

#include <string>

namespace StringExtend {
  using namespace std;

  typedef std::uint64_t hash_t;  
  constexpr hash_t prime = 0x100000001B3ull;  
  constexpr hash_t basis = 0xCBF29CE484222325ull;  

  constexpr hash_t string_hash(const char *str) {
    hash_t ret { basis };

    while (*str) {
      ret ^= *str;
      ret *= prime;
      str++;
    }

    return ret;
  }

  constexpr hash_t operator "" _hash(const char *str, size_t) {
    return string_hash(str);
  }

  hash_t hash_(std::string str);

  // 将int 转换成string 
  string itos(int i);
}