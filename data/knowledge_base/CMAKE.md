---
tags:
  - type/note
  - domain/prog/build-systems/cmake
---
Install and use the latest version of CMake (currently 3.27.7)

1. Installing CMake

First, let's install CMake on your computer. It's like getting a new toy, but for building cool software!

For Windows:
```
1. Go to https://cmake.org/download/
2. Click on "Windows x64 Installer" under the latest version
3. Download and run the installer
4. During installation, choose "Add CMake to the system PATH for all users"
5. Finish the installation
```

For macOS:
```
1. Open Terminal
2. If you don't have Homebrew, install it by pasting this:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
3. Then type: brew install cmake
```

For Linux:
```
1. Open Terminal
2. For Ubuntu or Debian, type: sudo apt-get install cmake
3. For Fedora, type: sudo dnf install cmake
```

2. Checking CMake Installation

Let's make sure CMake is installed correctly:

```bash
cmake --version
```

You should see something like "cmake version 3.27.7" or newer.

3. Your First CMake Project

Now, let's create your first CMake project! Imagine you're building a treehouse, but with code.

Create a new folder called "MyCoolProject" and go into it:

```bash
mkdir MyCoolProject
cd MyCoolProject
```

Now, let's create two files:

a) main.cpp (your cool code):
```cpp:main.cpp
#include <iostream>

int main() {
    std::cout << "Hello, CMake! I'm building cool stuff!" << std::endl;
    return 0;
}
```

b) CMakeLists.txt (your building instructions):
```cmake:CMakeLists.txt
cmake_minimum_required(VERSION 3.27)
project(MyCoolProject)

add_executable(MyCoolApp main.cpp)
```

4. Building Your Project

Time to build your treehouse! In your terminal, type:

```bash
cmake -S . -B build
cmake --build build
```

The first command is like drawing your treehouse plans, and the second one is actually building it!

5. Running Your Program

Your cool program is now built! Let's run it:

On Windows:
```
build\Debug\MyCoolApp.exe
```

On macOS or Linux:
```bash
./build/MyCoolApp
```

You should see: "Hello, CMake! I'm building cool stuff!"

Congratulations! You've just used CMake to build your first program. It's like using LEGO, but for making software. Each time you want to build a new project, you'll create a CMakeLists.txt file to tell CMake how to put your code together.

Next time, we can learn how to add more files to your project, like adding more rooms to your treehouse. Isn't that exciting?

### PLAN

Certainly! I'll modify the plan to focus on the latest version of CMake (currently 3.27.7) and structure it for a 10-year-old who's good at coding. We'll emphasize practical examples and fun projects to help you remember the concepts.

1. Getting Started with CMake
   - Installing the latest CMake (3.27.7) on Windows, macOS, and Linux
   - Your first CMake project: Building a "Hello, World!" program
   - CMake superhero challenge: Create a simple game using CMake

2. CMake Basics: Building Your Toolbox
   - Creating a CMakeLists.txt file: Your project's recipe
   - CMake commands: The magic words to build your software
   - Variables and properties: Storing important information
   - Fun project: Build a calculator program using CMake

3. Organizing Your Code Like a Pro
   - Folders and files: Keeping your code tidy
   - Adding subdirectories: Building a treehouse with many rooms
   - Libraries: Creating your own coding superpowers
   - Challenge: Build a multi-file project for a text-based adventure game

4. CMake Detective: Finding and Using Other People's Code
   - find_package(): Searching for coding treasures
   - Creating your own Find modules: Making a treasure map
   - Integrating external libraries: Adding superpowers to your project
   - Project: Build a weather app using an external API and CMake

5. Cross-Platform Ninja: One Code for All Computers
   - Writing CMake scripts that work everywhere
   - Handling different operating systems: Windows, macOS, and Linux
   - Creating builds that run on any computer
   - Challenge: Create a cross-platform GUI app for drawing

6. CMake Time Machine: Different Builds for Different Needs
   - Debug builds: Finding and fixing bugs
   - Release builds: Making your code super fast
   - Custom build types: Creating your own special builds
   - Project: Build a simple game with debug and release versions

7. Testing, Testing, 1-2-3: Making Sure Your Code Works
   - Adding tests to your project with CTest
   - Automatic testing: Robots that check your code
   - Measuring code coverage: How much of your code is tested?
   - Challenge: Create a math library with full test coverage

8. Packaging Your Code: Sharing Your Creations
   - Creating installable packages: Wrapping your code in a gift box
   - Generating documentation: Writing instructions for your code
   - Making distribution packages: Sending your code to others
   - Project: Package and share a small utility program

9. CMake Modules and Toolchains: Expanding Your Powers
   - Writing your own CMake modules: Creating new superpowers
   - Using toolchain files: Building code for different devices
   - Cross-compiling: Making your code run on other machines
   - Challenge: Create a CMake module for a custom build process

10. CMake Wizardry: Advanced Tricks and Tips
    - Generating code with CMake: Teaching CMake to write code
    - Custom commands and targets: Making CMake do anything
    - Debugging CMake scripts: Finding and fixing CMake problems
    - Project: Create a code generator using CMake

11. Modern C++ and CMake: The Dynamic Duo
    - Supporting the latest C++ features
    - Managing compiler flags: Telling the compiler what to do
    - Using package managers: Finding and using more code easily
    - Challenge: Build a modern C++ project using CMake and vcpkg

12. Real-World CMake Adventures
    - Building a cross-platform game engine
    - Creating a multi-language project (C++, Python, JavaScript)
    - Integrating with popular frameworks like Qt or wxWidgets
    - Final project: Design and build your own large-scale application


Sure! Let's use some fun analogies to explain the key concepts and details of CMake. Imagine we're building a LEGO project, and CMake is our instruction manual.

## Project: Cool Calculator

### 1. Project Setup

First, let's create a new project folder. Think of this as setting up your LEGO workspace:

```bash
mkdir CoolCalculator
cd CoolCalculator
```

### 2. Creating Source Files

We'll create two source files. These are like the LEGO pieces we'll use to build our project:

a) main.cpp
```cpp:main.cpp
#include <iostream>
#include "calculator.h"

int main() {
    Calculator calc;
    std::cout << "Welcome to Cool Calculator!" << std::endl;
    std::cout << "5 + 3 = " << calc.add(5, 3) << std::endl;
    std::cout << "10 - 4 = " << calc.subtract(10, 4) << std::endl;
    return 0;
}
```

b) calculator.cpp
```cpp:calculator.cpp
#include "calculator.h"

int Calculator::add(int a, int b) {
    return a + b;
}

int Calculator::subtract(int a, int b) {
    return a - b;
}
```

c) calculator.h
```cpp:calculator.h
#pragma once

class Calculator {
public:
    int add(int a, int b);
    int subtract(int a, int b);
};
```

### 3. Creating CMakeLists.txt

Now, let's create a CMakeLists.txt file that will build our calculator. This file is like the instruction manual for our LEGO project:

```cmake:CMakeLists.txt
# Set the minimum required version of CMake
cmake_minimum_required(VERSION 3.27)

# Set the project name and version
project(CoolCalculator VERSION 1.0)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Define a variable for our sources
set(SOURCES main.cpp calculator.cpp)

# Define a variable for include directories
set(INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR})

# Add an executable target
add_executable(calculator_app ${SOURCES})

# Add include directories
target_include_directories(calculator_app PUBLIC ${INCLUDE_DIRS})

# Print some information
message(STATUS "Project name: ${PROJECT_NAME}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Source files: ${SOURCES}")
```

### Breaking Down the CMakeLists.txt File

1. **cmake_minimum_required**: This is like telling CMake what version of LEGO bricks we need. We need at least version 3.27 to build our project.

2. **project**: This gives our project a name and version, like labeling our LEGO creation. Here, our project is called "CoolCalculator" and its version is 1.0.

3. **set(CMAKE_CXX_STANDARD 17)**: This tells CMake we want to use modern C++ features, like choosing a specific type of LEGO brick.

4. **set(SOURCES main.cpp calculator.cpp)**: This creates a variable called `SOURCES` containing our source files. It's like gathering all the LEGO pieces we need for our project.

5. **set(INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR})**: This creates a variable `INCLUDE_DIRS` with the current source directory. It's like telling CMake where to find our LEGO pieces.

6. **add_executable**: This command tells CMake to create a program from our source files. It's like assembling our LEGO pieces into the final model.

7. **target_include_directories**: This tells CMake where to find our header files. It's like providing a map to the LEGO pieces.

8. **message(STATUS "...")**: This command prints information during the CMake configuration process. It's like getting updates on our LEGO project's progress.

### 4. Building the Project

Now, let's build our calculator. This step is like following the LEGO instructions to build our model:

```bash
cmake -S . -B build
cmake --build build
```

### 5. Running the Program

Run your calculator program. This is like playing with your completed LEGO model:

On Windows:
```
build\Debug\calculator_app.exe
```

On macOS or Linux:
```bash
./build/calculator_app
```

You should see:
```
Welcome to Cool Calculator!
5 + 3 = 8
10 - 4 = 6
```

### Key Concepts and Details

1. **CMake Commands**:
   - `cmake_minimum_required`: Sets the minimum version of CMake required. (Choosing the right LEGO set)
   - `project`: Defines the project name and version. (Labeling your LEGO creation)
   - `set`: Assigns values to variables. (Gathering LEGO pieces)
   - `add_executable`: Creates an executable target. (Assembling the LEGO model)
   - `target_include_directories`: Specifies include directories for a target. (Providing a map to the LEGO pieces)
   - `message`: Prints messages during configuration. (Getting updates on your LEGO project's progress)

2. **Variables**:
   - User-defined: `SOURCES`, `INCLUDE_DIRS` (Your custom LEGO pieces)
   - Predefined: `CMAKE_CXX_STANDARD`, `CMAKE_CURRENT_SOURCE_DIR`, `PROJECT_NAME` (Standard LEGO pieces)
   - Referenced using `${VARIABLE_NAME}` syntax. (Using the right LEGO pieces)

3. **Naming Conventions**:
   - Predefined CMake commands and variables use lowercase with underscores. (Standard LEGO instructions)
   - User-defined variables typically use UPPERCASE. (Your custom LEGO instructions)
   - Project and target names are user-defined and can use mixed case. (Naming your LEGO creation)

4. **File Organization**:
   - Separate source files (.cpp) and header files (.h). (Organizing your LEGO pieces)
   - CMakeLists.txt in the project root directory. (Your LEGO instruction manual)

5. **C++ Standard Setting**:
   - Use `set(CMAKE_CXX_STANDARD xx)` to specify the C++ standard. (Choosing the right LEGO bricks)
   - `CMAKE_CXX_STANDARD_REQUIRED True` ensures the specified standard is used. (Making sure you have the right LEGO bricks)

6. **Build Process**:
   - Configuration step: `cmake -S . -B build` (Planning your LEGO project)
   - Build step: `cmake --build build` (Building your LEGO model)

7. **Targets**:
   - Executables are created with `add_executable`. (Assembling the LEGO model)
   - The target name (e.g., `calculator_app`) is used to refer to the executable. (Naming your LEGO model)

8. **Include Directories**:
   - `target_include_directories` specifies where to find header files. (Providing a map to the LEGO pieces)
   - `PUBLIC` keyword makes the include directories available to targets that link to this one. (Sharing your LEGO pieces)

9. **CMake Variables vs C++ Variables**:
   - CMake variables (like `SOURCES`) are used during the build configuration. (Gathering LEGO pieces)
   - They're different from C++ variables used in the actual code. (Using LEGO pieces in your model)

10. **CMake's Role**:
    - CMake generates platform-specific build files (e.g., Makefiles, Visual Studio projects). (Creating LEGO instructions for different sets)
    - It doesn't compile the code directly but creates the instructions for the native build system. (Providing the LEGO instructions)

11. **Cross-Platform Considerations**:
    - CMake uses forward slashes (/) for paths, even on Windows. (Using the same LEGO instructions for different sets)
    - Use `${CMAKE_CURRENT_SOURCE_DIR}` for portable paths. (Making sure your LEGO instructions work everywhere)

12. **Debugging CMake**:
    - Use `message()` to print variable values and debug information. (Getting updates on your LEGO project's progress)
    - Different message types: STATUS, WARNING, FATAL_ERROR. (Different types of LEGO instructions)

13. **Best Practices**:
    - Keep CMakeLists.txt clean and organized. (Keeping your LEGO instructions tidy)
    - Use variables to group related items (like source files). (Organizing your LEGO pieces)
    - Comment your CMake code for clarity. (Adding notes to your LEGO instructions)

14. **Next Steps**:
    - Explore more complex project structures. (Building more advanced LEGO models)
    - Learn about creating and linking libraries. (Adding more LEGO sets to your collection)
    - Investigate conditional compilation and platform-specific code. (Customizing your LEGO instructions for different sets)

CMake offers several benefits beyond just automating the build process. Let's explore these benefits and understand how CMake achieves cross-platform compatibility internally.

### Benefits of Using CMake

1. **Cross-Platform Compatibility**:
   - CMake generates native build files for different platforms (e.g., Makefiles for Unix, Visual Studio projects for Windows, Xcode projects for macOS).
   - This allows you to write your build configuration once and use it on multiple platforms without modification.

2. **Simplified Build Configuration**:
   - CMake provides a high-level language to describe the build process, making it easier to manage complex projects.
   - It abstracts away the details of the underlying build system, allowing you to focus on the structure of your project.

3. **Dependency Management**:
   - CMake can find and manage dependencies automatically using the `find_package()` command.
   - It supports external libraries and can handle version checks, ensuring that the correct versions of dependencies are used.

4. **Modular and Scalable**:
   - CMake supports modular project structures, allowing you to break down large projects into smaller, manageable components.
   - It can handle projects with multiple subdirectories and libraries, making it suitable for large-scale software development.

5. **Customizable and Extensible**:
   - CMake allows you to define custom commands and targets, providing flexibility to tailor the build process to your needs.
   - You can write your own CMake modules and functions to extend its capabilities.

6. **Integration with Testing and Packaging**:
   - CMake integrates with testing frameworks like CTest, enabling you to add automated tests to your project.
   - It supports packaging and installation, allowing you to create installable packages for your software.

### How CMake Achieves Cross-Platform Compatibility

CMake achieves cross-platform compatibility through several mechanisms:

1. **Abstracting Build Systems**:
   - CMake abstracts the details of the underlying build system (e.g., Make, Ninja, Visual Studio).
   - It provides a unified interface to describe the build process, which is then translated into platform-specific build files.

2. **Platform-Specific Generators**:
   - CMake uses generators to create build files for different platforms.
   - When you run the `cmake` command, you specify a generator (e.g., `Unix Makefiles`, `Ninja`, `Visual Studio`) that determines the type of build files to generate.

3. **Built-in Platform Checks**:
   - CMake has built-in checks to detect the operating system, compiler, and other environment details.
   - It uses this information to adjust the build configuration accordingly, ensuring compatibility with the target platform.

4. **Portable Path Handling**:
   - CMake uses forward slashes (/) for paths, even on Windows, to ensure consistency across platforms.
   - It provides variables like `CMAKE_CURRENT_SOURCE_DIR` to handle paths in a portable manner.

5. **Conditional Compilation**:
   - CMake supports conditional statements (e.g., `if`, `elseif`, `else`) to handle platform-specific code.
   - You can use these statements to include or exclude certain files or settings based on the target platform.

6. **Toolchain Files**:
   - CMake allows you to use toolchain files to specify the compiler and tools for cross-compiling.
   - This is useful for building software for different architectures or embedded systems.

### Example: Cross-Platform Project

Let's create a simple cross-platform project to see how CMake handles different platforms.

#### Project Setup

```bash
mkdir CrossPlatformApp
cd CrossPlatformApp
```

#### Source Files

a) main.cpp
```cpp:main.cpp
#include <iostream>

int main() {
    std::cout << "Hello, Cross-Platform World!" << std::endl;
    return 0;
}
```

#### CMakeLists.txt

```cmake:CMakeLists.txt
cmake_minimum_required(VERSION 3.27)
project(CrossPlatformApp VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_executable(CrossPlatformApp main.cpp)

# Platform-specific settings
if(WIN32)
    message(STATUS "Configuring for Windows")
    # Windows-specific settings
elseif(APPLE)
    message(STATUS "Configuring for macOS")
    # macOS-specific settings
elseif(UNIX)
    message(STATUS "Configuring for Unix/Linux")
    # Unix/Linux-specific settings
endif()
```

#### Building the Project

1. **On Windows (Visual Studio)**:
   ```bash
   cmake -G "Visual Studio 16 2019" -S . -B build
   cmake --build build
   ```

2. **On macOS (Xcode)**:
   ```bash
   cmake -G "Xcode" -S . -B build
   cmake --build build
   ```

3. **On Linux (Makefiles)**:
   ```bash
   cmake -G "Unix Makefiles" -S . -B build
   cmake --build build
   ```

### Explanation

1. **Abstracting Build Systems**:
   - The `cmake_minimum_required` and `project` commands set up the project in a platform-independent way.
   - The `add_executable` command creates an executable target, abstracting the details of the underlying build system.

2. **Platform-Specific Generators**:
   - The `-G` option specifies the generator to use, allowing CMake to create the appropriate build files for each platform.

3. **Built-in Platform Checks**:
   - The `if(WIN32)`, `elseif(APPLE)`, and `elseif(UNIX)` statements allow you to add platform-specific settings.

4. **Portable Path Handling**:
   - CMake uses forward slashes for paths, ensuring consistency across platforms.

5. **Conditional Compilation**:
   - The conditional statements in the CMakeLists.txt file allow you to customize the build process for different platforms.


---


## 3. Organizing Your Code Like a Pro

### Folders and Files: Keeping Your Code Tidy

Imagine your project is a big LEGO set. To keep things tidy, you need to organize your LEGO pieces into different boxes. Similarly, in a coding project, you organize your source files into different folders.

### Adding Subdirectories: Building a Treehouse with Many Rooms

Let's extend our CoolCalculator project by adding a new feature: a scientific calculator. We'll organize our project into subdirectories to keep things tidy.

#### Project Setup

First, let's create a new project folder structure:

```bash
mkdir -p CoolCalculator/src
mkdir -p CoolCalculator/include
mkdir -p CoolCalculator/src/scientific
cd CoolCalculator
```

#### Source Files

a) main.cpp
```cpp:src/main.cpp
#include <iostream>
#include "calculator.h"
#include "scientific_calculator.h"

int main() {
    Calculator calc;
    ScientificCalculator sciCalc;

    std::cout << "Welcome to Cool Calculator!" << std::endl;
    std::cout << "5 + 3 = " << calc.add(5, 3) << std::endl;
    std::cout << "10 - 4 = " << calc.subtract(10, 4) << std::endl;
    std::cout << "sin(30) = " << sciCalc.sin(30) << std::endl;

    return 0;
}
```

b) calculator.cpp
```cpp:src/calculator.cpp
#include "calculator.h"

int Calculator::add(int a, int b) {
    return a + b;
}

int Calculator::subtract(int a, int b) {
    return a - b;
}
```

c) calculator.h
```cpp:include/calculator.h
#pragma once

class Calculator {
public:
    int add(int a, int b);
    int subtract(int a, int b);
};
```

d) scientific_calculator.cpp
```cpp:src/scientific/scientific_calculator.cpp
#include "scientific_calculator.h"
#include <cmath>

double ScientificCalculator::sin(double angle) {
    return std::sin(angle);
}
```

e) scientific_calculator.h
```cpp:include/scientific_calculator.h
#pragma once

class ScientificCalculator {
public:
    double sin(double angle);
};
```

### Creating CMakeLists.txt

Now, let's create a CMakeLists.txt file that will build our calculator. We'll add subdirectories to organize our project.

```cmake:CMakeLists.txt
cmake_minimum_required(VERSION 3.27)
project(CoolCalculator VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Include directories
include_directories(include)

# Add subdirectories
add_subdirectory(src)

# Add an executable target
add_executable(calculator_app src/main.cpp)

# Link libraries
target_link_libraries(calculator_app calculator scientific_calculator)
```

### Creating CMakeLists.txt for Subdirectories

We'll create separate CMakeLists.txt files for the `src` and `scientific` subdirectories.

#### src/CMakeLists.txt
```cmake:src/CMakeLists.txt
# Add subdirectory for scientific calculator
add_subdirectory(scientific)

# Add library for basic calculator
add_library(calculator calculator.cpp)
```

#### src/scientific/CMakeLists.txt
```cmake:src/scientific/CMakeLists.txt
# Add library for scientific calculator
add_library(scientific_calculator scientific_calculator.cpp)
```

### Building the Project

Now, let's build our calculator:

```bash
cmake -S . -B build
cmake --build build
```

### Running the Program

Run your calculator program:

On Windows:
```
build\Debug\calculator_app.exe
```

On macOS or Linux:
```bash
./build/calculator_app
```

You should see:
```
Welcome to Cool Calculator!
5 + 3 = 8
10 - 4 = 6
sin(30) = 0.5
```

### Possible Errors and Solutions

1. **Missing Header Files**:
   - Error: `fatal error: 'calculator.h' file not found`
   - Solution: Ensure the `include_directories` command in the root CMakeLists.txt file points to the correct include directory.

2. **Linking Errors**:
   - Error: `undefined reference to 'Calculator::add(int, int)'`
   - Solution: Ensure the `target_link_libraries` command in the root CMakeLists.txt file links the correct libraries.

3. **Incorrect File Paths**:
   - Error: `CMake Error: Cannot find source file: src/main.cpp`
   - Solution: Verify the file paths in the `add_executable` and `add_library` commands are correct.

### How CMake Makes It Easier

Without CMake, you would have to manually write platform-specific build scripts (e.g., Makefiles for Unix, Visual Studio project files for Windows). This would involve:

- Manually specifying compiler and linker flags.
- Handling dependencies and include directories.
- Writing custom scripts for different platforms.
- Managing complex build configurations and dependencies.

CMake simplifies this by:

- Providing a high-level language to describe the build process.
- Automatically generating platform-specific build files.
- Managing dependencies and include directories.
- Allowing you to write modular and scalable build configurations.

### Summary
By organizing your code into subdirectories and using CMake to manage the build process, you can keep your project tidy and scalable. CMake's ability to generate platform-specific build files and manage dependencies makes it a powerful tool for cross-platform development.

---

---
Parent MOC: [[CMAKE MOC]]