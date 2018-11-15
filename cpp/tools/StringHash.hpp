#pragma once

#include <string>

typedef std::uint64_t hash_t;  
constexpr hash_t prime = 0x100000001B3ull;  
constexpr hash_t basis = 0xCBF29CE484222325ull;  

constexpr unsigned long long operator "" _hash(const char *str, size_t) {
  hash_t ret { basis };

  while(*str) {
      ret ^= *str;
      ret *= prime;
      str++;
  }

  return ret;
}

hash_t hash_(std::string str);