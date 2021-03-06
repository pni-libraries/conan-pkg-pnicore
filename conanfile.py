from conans import ConanFile, CMake, tools
import os
import git


class PnicoreConan(ConanFile):
    """
    Building the pnicore library from a the current repository. 
    """
    #
    # set this to the appropriate library version and deactivate 
    # auto_update for stables releases
    #
    version = "master"
    auto_update = True
    
    #
    # this could be left unchanged for virtually all stable and developer
    # releases.
    #
    name = "pnicore"
    license = "GPL V2"
    url = "https://github.com/pni-libraries/conan-pkg-pnicore"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_system_boost":[True,False],
               "commit":"ANY"}
    default_options = "shared=True","with_system_boost=False","commit=0"
    generators = "cmake"
    build_policy="missing"
    description = """
    Package builds the current master branch of the pnicore library.
    This is intended for developers which want to work with this development
    tree. The master brachn is considered to always build.
    """

    boost_package = "Boost/1.62.0@lasote/stable"
    zlib_package = "zlib/1.2.8@conan/stable"
    bzip2_package = "bzip2/1.0.6@conan/stable"
    pnicore_git_url = "https://github.com/pni-libraries/libpnicore.git"
    
    def _current_remote_commit(self):
        self.output.info("Trying to get latest commit from remote repository")
        gcmd = git.cmd.Git()
        commit = None
        
        try:
            commit = gcmd.ls_remote(self.pnicore_git_url,"refs/heads/master").split("\t")[0]
            self.output.info("The current remote master is on: %s" %commit)
        except:
            self.output.info("Failure to determine the current commit from remote")
            
        return commit
        
    def configure(self):
        self.output.info("Setting the configuration")
        #setting up boost if required
        self.requires(self.boost_package)
        self.requires(self.zlib_package)
        self.requires(self.bzip2_package)
        
        self.options["Boost"].shared=True
        self.options["zlib"].shared=True
            
        if self.auto_update: 
            self.options.commit = self._current_remote_commit()
        

    def source(self):
        self.output.info("Cloning git repository")
        self.run("git clone %s" %self.pnicore_git_url)
        self.run("cd libpnicore && git submodule init && git submodule update --remote")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly



    def build(self):
        #
        # pulling from the original repository 
        #
        self.output.info("Running the build")
        self.output.info("pull from the master branch ...")
        self.run("cd libpnicore && git pull")
        
        #
        # patching the sources before the build
        #
        self.output.info("patching CMakeLists.txt ...")
        tools.replace_in_file("libpnicore/CMakeLists.txt", "include(CTest)",
'''
include(CTest)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
'''
        )
        
        #
        # Running cmake and perform the build
        #
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"]="ON"


        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type

        cmake.configure(source_dir="libpnicore")
        cmake.build()

        cmake.build(target="install")


    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = ["pnicore"]

    def imports(self):
        #on windows we copy the files to the bin directory
        if self.settings.os=="Windows":
            self.copy("*.dll","bin","bin")
        elif self.settings.os=="Linux":
            self.copy("*.so","lib","lib")
