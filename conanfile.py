from conans import ConanFile, CMake, tools
import os


class PnicoreConan(ConanFile):
    name = "pnicore"
    version = "1.1.0"
    license = "GPL V2"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_system_boost":[True,False]}
    default_options = "shared=True","with_system_boost=False"
    generators = "cmake"
    build_policy="missing"
    description = """
    Package builds the current master branch of the pnicore library.
    This is intended for developers which want to work with this development
    tree. The master brachn is considered to always build.
    """

    boost_package = "Boost/1.62.0@lasote/stable"

    def configure(self):
        #setting up boost if required
        if not self.options.with_system_boost:
            self.requires(self.boost_package)

            self.options["Boost"].shared = self.options.shared

    def source(self):
        self.run("git clone https://github.com/pni-libraries/libpnicore.git")
        self.run("cd libpnicore && git submodule init && git submodule update --remote")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("libpnicore/CMakeLists.txt", "include(CTest)",
'''
include(CTest)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
'''
        )


    def build(self):
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"]="ON"



        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type

        cmake.configure(source_dir="libpnicore")

        cmake.build()

        if self.settings.os=="Windows":
            cmake.build(target="RUN_TESTS")
        else:
            cmake.build(target="test")


        cmake.build(target="install")


    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["pnicore"]

    def imports(self):
        #on windows we copy the files to the bin directory
        if self.settings.os=="Windows":
            self.copy("*.dll","bin","bin")
