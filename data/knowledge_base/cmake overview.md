---
tags:
  - type/note
  - domain/prog/build-systems/cmake
---
CMakeLists.txt file section by section, explaining each command, its purpose, and alternative options.

# CMakeLists.txt Detailed Explanation

## 1. Basic Project Setup
```cmake
cmake_minimum_required(VERSION 3.16)
```
- **Purpose**: Specifies the minimum CMake version required
- **Why**: Ensures compatibility and access to required features
- **Alternative**: You can use higher versions for newer features
- **Best Practice**: Always specify this at the top of your CMakeLists.txt

```cmake
project(TPMProject C)
```
- **Purpose**: Defines project name and primary language
- **Parameters**:
  - First argument: Project name
  - Second argument: Primary language (C, CXX, etc.)
- **Alternative**: `project(TPMProject C CXX)` for multi-language projects
- **What it sets**:
  - `PROJECT_NAME`: Your project name
  - `CMAKE_PROJECT_VERSION`: Project version (if specified)
  - `PROJECT_SOURCE_DIR`: Source directory path

## 2. Architecture Configuration
```cmake
set(ARCH "arm32" CACHE STRING "Target Architecture (arm32 or arm64)")
```
- **Purpose**: Creates a cached variable for architecture selection
- **Parameters**:
  - Variable name: `ARCH`
  - Default value: `"arm32"`
  - Type: `STRING`
  - Description: Help text for CMake GUI
- **Usage**: Can be set via command line: `-DARCH=arm64`
- **Alternative**: Could use `option()` for boolean flags

## 3. Conditional Configuration
```cmake
if(ARCH STREQUAL "arm32")
    set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
    set(OPENSSL_ROOT ${CMAKE_SOURCE_DIR}/openssl-arm32)
elseif(ARCH STREQUAL "arm64")
    set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
    set(OPENSSL_ROOT ${CMAKE_SOURCE_DIR}/openssl-arm64)
else()
    message(FATAL_ERROR "Unsupported ARCH: ${ARCH}")
endif()
```
- **Purpose**: Sets compiler and paths based on architecture
- **Key Variables**:
  - `CMAKE_C_COMPILER`: Specifies the C compiler
  - `CMAKE_SOURCE_DIR`: Root source directory
- **Alternative Conditions**:
  - `if(DEFINED variable)`: Check if variable exists
  - `if(variable MATCHES regex)`: Pattern matching
  - `if(EXISTS path)`: Check if file/directory exists

## 4. Include Directories
```cmake
include_directories(
    ${OPENSSL_ROOT}/include
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/comm_module
)
```
- **Purpose**: Adds include paths for the compiler
- **Alternative**: Modern approach using `target_include_directories()`
```cmake
target_include_directories(tpm_binary PRIVATE
    ${OPENSSL_ROOT}/include
    ${CMAKE_SOURCE_DIR}/src
)
```
- **Visibility Options**:
  - `PUBLIC`: For target and its dependencies
  - `PRIVATE`: Only for target
  - `INTERFACE`: Only for dependencies

## 5. Source Files
```cmake
file(GLOB SOURCES 
    "src/*.c"
    "src/comm_module/*.c"
)
```
- **Purpose**: Collects source files automatically
- **Warning**: GLOB is not recommended for CMake best practices
- **Alternative**: Explicit file listing
```cmake
set(SOURCES
    src/main.c
    src/comm_module/comm.c
)
```

## 6. Conditional Source Management
```cmake
if(UNIX)
    list(REMOVE_ITEM SOURCES
        ${CMAKE_SOURCE_DIR}/src/TcpServer.c
        ${CMAKE_SOURCE_DIR}/src/applink.c
        ${CMAKE_SOURCE_DIR}/src/TPMCmds.c
    )
    list(APPEND SOURCES
        ${CMAKE_SOURCE_DIR}/src/TcpServerPosix.c
    )
endif()
```
- **Purpose**: Platform-specific source file management
- **Commands**:
  - `list(REMOVE_ITEM ...)`: Removes items from list
  - `list(APPEND ...)`: Adds items to list
- **Alternative**: Could use `target_sources()` for modern CMake

## 7. Executable Definition
```cmake
add_executable(tpm_binary ${SOURCES})
```
- **Purpose**: Creates an executable target
- **Parameters**:
  - First argument: Target name
  - Second argument: Source files
- **Alternative**: For libraries
```cmake
add_library(mylib STATIC ${SOURCES})  # Static library
add_library(mylib SHARED ${SOURCES})  # Shared library
```

## 8. Compile Definitions
```cmake
target_compile_definitions(tpm_binary PRIVATE
    NO_MD4
    NO_MD5
    NO_DH
    NO_DSA
    OPENSSL_NO_DEPRECATED_3_0
    FAIL_TRACE
)
```
- **Purpose**: Adds preprocessor definitions
- **Visibility**: Same as include directories (PUBLIC/PRIVATE/INTERFACE)
- **Alternative**: Global definitions
```cmake
add_definitions(-DNO_MD4 -DNO_MD5)
```

## 9. Static Linking
```cmake
target_link_libraries(tpm_binary 
    -static
    -Wl,--whole-archive
    ${OPENSSL_ROOT}/lib/libssl.a
    ${OPENSSL_ROOT}/lib/libcrypto.a
    -Wl,--no-whole-archive
)
```
- **Purpose**: Links libraries to the target
- **Flags**:
  - `-static`: Force static linking
  - `-Wl,--whole-archive`: Include all symbols
- **Alternative**: Dynamic linking
```cmake
target_link_libraries(tpm_binary PRIVATE ssl crypto)
```

## 10. Build Properties
```cmake
set_target_properties(tpm_binary PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
)
```
- **Purpose**: Sets target-specific properties
- **Common Properties**:
  - `C_STANDARD`: C standard version
  - `CXX_STANDARD`: C++ standard version
  - `POSITION_INDEPENDENT_CODE`: For shared libraries
- **Alternative**: Global properties
```cmake
set(CMAKE_C_STANDARD 11)
```

## 11. Compiler Options
```cmake
target_compile_options(tpm_binary PRIVATE -Wall -Wextra)
```
- **Purpose**: Adds compiler flags
- **Common Options**:
  - `-Wall`: Enable all warnings
  - `-Wextra`: Enable extra warnings
  - `-O2`: Optimization level
- **Alternative**: Global options
```cmake
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")
```

---

Here is a **complete, structured, and detailed guide** on:

---

## 🔁 **CMake Command Order**

**Which commands must go before/after others**, with reasons, common practices, and variations.

Also includes **real project structure best practices** with modular or monolithic builds.

---

# ✅ BASIC STRUCTURE & ORDERING

### 🧾 A typical `CMakeLists.txt` should follow this order:

```
1. cmake_minimum_required
2. project
3. global settings (C/C++ standards, output dirs)
4. include custom modules (optional)
5. find_package (external dependencies)
6. include_directories / link_directories (legacy - avoid)
7. add_subdirectory / add_library / add_executable
8. target_include_directories
9. target_compile_definitions / target_compile_options
10. target_link_libraries
11. install() / testing() / custom_commands()
```

---

### 🔁 ORDER MATTERS: EXPLANATION

| Step | Command(s)                                                       | Must Come **Before**                    | Reason                                               |
| ---- | ---------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------- |
| 1    | `cmake_minimum_required()`                                       | Everything                              | Initializes CMake version requirements               |
| 2    | `project(...)`                                                   | Everything else                         | Sets project-wide settings and variables             |
| 3    | `set(CMAKE_C_STANDARD ...)`<br>`set(CMAKE_OUTPUT_DIRECTORY ...)` | `add_library` or `add_executable`       | These affect how and where targets are compiled      |
| 4    | `include(...)` (custom cmake scripts)                            | before target defs                      | Needed to load functions/macros                      |
| 5    | `find_package(...)`                                              | before linking targets                  | External libraries must be found before use          |
| 6    | `add_subdirectory(...)`                                          | before defining dependencies on subdirs | Adds child CMakeLists to parse                       |
| 7    | `add_library(...)`, `add_executable(...)`                        | before configuring them                 | You can't configure a target that doesn't exist      |
| 8    | `target_include_directories(...)`                                | after target is added                   | Target must exist first                              |
| 9    | `target_compile_definitions`, `target_compile_options`           | after target is added                   | Same reason as above                                 |
| 10   | `target_link_libraries(...)`                                     | after library/executable is created     | You must link to an existing target                  |
| 11   | `install(...)`, `enable_testing()`                               | end                                     | For packaging or testing the already defined targets |

---

# 🔧 PRACTICAL EXAMPLES

---

## 🧩 Minimal Static Library Project

```cmake
cmake_minimum_required(VERSION 3.16)  # [1]
project(MyLibProject LANGUAGES C)     # [2]

set(CMAKE_C_STANDARD 99)              # [3]
set(CMAKE_C_STANDARD_REQUIRED ON)

file(GLOB SRC_FILES src/*.c)          # [7] (prepare file list)

add_library(mylib STATIC ${SRC_FILES})       # [7] (define target)

target_include_directories(mylib              # [8]
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

target_compile_definitions(mylib PRIVATE USE_FAST)  # [9]

# Optional install step
install(TARGETS mylib DESTINATION lib)        # [11]
install(DIRECTORY include/ DESTINATION include)
```

---

## 🧩 Application Using Static Lib

```cmake
cmake_minimum_required(VERSION 3.16)
project(MyApp LANGUAGES C)

set(CMAKE_C_STANDARD 99)

add_subdirectory(lib_mylib)           # [6] Must be before linking to mylib

add_executable(my_app main.c)         # [7]

target_include_directories(my_app PRIVATE ${CMAKE_SOURCE_DIR}/include)  # [8]
target_link_libraries(my_app PRIVATE mylib)                              # [10]
```

---

## 🔁 Correct vs Incorrect Orders

### ❌ Wrong

```cmake
target_link_libraries(my_app PRIVATE mylib)
add_executable(my_app main.c)
```

This fails because you try to link a target **before defining it**.

---

### ✅ Correct

```cmake
add_executable(my_app main.c)
target_link_libraries(my_app PRIVATE mylib)
```

---

# 🛠️ ADVANCED CASES

---

## 📦 External Library with `find_package()`

```cmake
# Must go before target_link_libraries
find_package(OpenSSL REQUIRED)

add_executable(secure_app main.c)

target_link_libraries(secure_app PRIVATE OpenSSL::SSL OpenSSL::Crypto)
```

---

## 🧪 Adding Unit Tests

```cmake
enable_testing()

add_executable(test_foo test/test_foo.c)
target_link_libraries(test_foo PRIVATE mylib)

add_test(NAME FooTest COMMAND test_foo)
```

---

# 📌 Best Practices Summary Table

| Practice                                                                  | Recommended? | Reason                                            |
| ------------------------------------------------------------------------- | ------------ | ------------------------------------------------- |
| Use `target_*` over global `include_directories`, `link_libraries`        | ✅            | Modern CMake is target-centric                    |
| Always define targets before configuring them                             | ✅            | Ensures CMake does not error                      |
| Use `add_subdirectory()` for your own code, `find_package()` for external | ✅            | Clean dependency control                          |
| Keep external libs in `lib/` or use package managers like `vcpkg`/`conan` | ✅            | Easier to maintain and build                      |
| Avoid `link_directories()` unless absolutely necessary                    | ❌            | Can lead to ambiguous behavior                    |
| Avoid `file(GLOB ...)` for production builds                              | ⚠️           | May not catch renamed files in incremental builds |

---

# 🧠 Final Advice

* **Think of CMake as target-oriented and layered**
* Always **define targets**, then **configure them**, then **link them**
* Order is not just syntactic—it affects the dependency graph
* **Modularize**: split large projects using `add_subdirectory()` and per-folder `CMakeLists.txt`

---

---
Parent MOC: [[CMAKE MOC]]