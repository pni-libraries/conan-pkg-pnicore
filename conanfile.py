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
    url = "<Package recipe repository url here, for issues about the package>"
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
    pnicore_git_url = "https://github.com/pni-libraries/libpnicore.git"
    
    def _get_local_current_commit(self,repository_path):
        self.output.info("Trying to access repository in: "+repository_path)
        commit = None
        try:
            self.run("cd %s && git pull" %repository_path) 
            repo = git.Repo(repository_path)
            commit = repo.commit().hexsha
            self.output.info("Current commit is: "+commit)
            
        except:
            self.output.info("Could not retrieve current commit of sources")
            
        return commit
    
    def _get_remote_current_commit(self):
        self.output.info("Trying to get latest commit from remote repository")
        gcmd = git.cmd.Git()
        commit = None
        
        try:
            commit = gcmd.ls_remote(self.pnicore_git_url,"refs/heads/master").split("\t")[0]
            self.output.info("The current remote master is on: %s" %commit)
        except:
            self.output("Failure to determine the current commit from remote")
            
        return commit
    
    def _get_current_commit(self):
        #we pull here the repository and add the commit to the build options. 
        #if the commit has changed the hash of the build configuration will change
        #and thus force a rebuild of the package
        
        
        current_commit = None
        self.output.info("Checking the GIT commit")       
        source_path =  os.path.join(self.conanfile_directory,"..","source","libpnicore")
        
        if os.path.exists(source_path):
            current_commit = self._get_local_current_commit(source_path)
        else:
            current_commit = self._get_remote_current_commit()
            
        return current_commit
    
    def _set_commit_option(self):
        current_commit = self._get_current_commit()
        if current_commit != None:
            #if we can obtain the actual commit of the repository we can do something with it
            self.options.commit = current_commit
        
    def configure(self):
        self.output.info("Setting the configuration")
        #setting up boost if required
        if not self.options.with_system_boost:
            self.requires(self.boost_package)

            self.options["Boost"].shared = self.options.shared
            
        if self.auto_update: self._set_commit_option()
        

    def source(self):
        self.output.info("Cloning git repository")
        self.run("git clone %s" %self.pnicore_git_url)
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
        
        if self.auto_update: self._set_commit_option()


    def build(self):
        self.output.info("Running the build")
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
