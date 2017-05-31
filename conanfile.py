from conans import ConanFile, CMake, tools
import os


class PnicoreConan(ConanFile):
    name = "pnicore"
    requires = "Boost/1.64.0@wintersb/stable"
    version = "1.1.0"
    license = "GPL V2"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_conan_boost":[True,False]}
    default_options = "shared=True","with_conan_boost=False"
    generators = "cmake"
    build_policy="always"
    description = """
    Package builds the current master branch of the pnicore library.
    This is intended for developers which want to work with this development
    tree. The master brachn is considered to always build.
    """

    def source(self):
        self.run("git clone https://github.com/pni-libraries/libpnicore.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
#        tools.replace_in_file("libpnicore/CMakeLists.txt", "include(CTest)",
#'''
#include(CTest)
#include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
#conan_basic_setup()
#'''
#)

    def build(self):
        cmake = CMake(self)
        cmake_defs = {}

        if self.options.shared:
            cmake_defs["BUILD_SHARED_LIBS"]="ON"

        if self.options.with_conan_boost:
            self.output.info("PNICORE will be built with conan provided Boost")
            cmake_defs["PNICORE_CONAN_BOOST"] = "ON"
        else:
            self.output.info("PNICORE will be built with system boost libraries")

        cmake_defs["CMAKE_INSTALL_PREFIX"] = self.package_folder

        cmake.configure(source_dir="libpnicore",
                        defs=cmake_defs)

        cmake.build(target="all")
        cmake.build(target="test")
        cmake.build(target="install")


    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["pnicore"]
