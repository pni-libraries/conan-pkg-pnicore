# conan-pkg-pnicore
A conan package for the pnicore library

This is a conan package for the ``pnicore`` library. 

## Getting the right package  

There are several ways how to use this package depending on from which 
branch you are taking it. 

* if you clone from master you get a *rolling* package which keeps up to date 
  with the current master branch of the ``pnicore`` libraries upstream repository
* if you use one of the version branches you get a conan package for a particular 
  released version of ``pnicore``.  

### Using master 

If you simply clone the repository and use the package in the master branch you will get 
something like a *rolling* release of ``pnicore``. The package is configured so that it 
rebuilds itself every time a new commit has been pushed to the master branch of ``pniio`'s 
upstream repository. 
The updating mechanism is rather simple: the actual commit is added to the build options 
of the package and thus contributes to the SHA key of the current build. If none of the 
build settings and options change but a new commit is available this will change the SHA 
key and thus trigger a rebuild of the package. 

This version of the package is mainly intersting for developers who want to keep their 
code up to date with new features implemented in ``libpnicore``. However, I do not recommend 
to use this package for production builds. For the latter situations use one of the 
version branches. 

### Using version branches



