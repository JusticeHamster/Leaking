#include <sys/stat.h>
#include <stdio.h>
#include <unistd.h>

static inline int os_mkdir(const char *path) {
    return mkdir(path, 0777);
}
static inline bool os_exists(const char *path) {
    return access(path, F_OK) != -1;
}