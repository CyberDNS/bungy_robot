
ROS 2 Distro | Branch | Build status | Documentation | Released packages
:---------: | :----: | :----------: | :-----------: | :---------------:
**Humble** | [`humble`](https://github.com/CyberDNS/bungy_robot/tree/humble) | [![Humble Binary Build](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-binary-build-main.yml/badge.svg?branch=main)](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-binary-build-main.yml?branch=main) <br /> [![Humble Binary Build](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-binary-build-testing.yml/badge.svg?branch=main)](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-binary-build-testing.yml?branch=main) <br /> [![Humble Semi-Binary Build](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-semi-binary-build-main.yml/badge.svg?branch=main)](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-semi-binary-build-main.yml?branch=main) <br /> [![Humble Semi-Binary Build](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-semi-binary-build-testing.yml/badge.svg?branch=main)](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-semi-binary-build-testing.yml?branch=main) <br /> [![Humble Source Build](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-source-build.yml/badge.svg?branch=main)](https://github.com/CyberDNS/bungy_robot/actions/workflows/humble-source-build.yml?branch=main) | [![Doxygen Doc Deployment](https://github.com/CyberDNS/bungy_robot/actions/workflows/doxygen-deploy.yml/badge.svg)](https://github.com/CyberDNS/bungy_robot/actions/workflows/doxygen-deploy.yml) <br /> [Generated Doc](https://CyberDNS.github.io/bungy_robot_Documentation/humble/html/index.html) | [bungy_robot](https://index.ros.org/p/bungy_robot/#humble)

## Build status


### Explanation of different build types

**NOTE**: There are three build stages checking current and future compatibility of the package.

[Detailed build status](.github/workflows/README.md)

1. Binary builds - against released packages (main and testing) in ROS distributions. Shows that direct local build is possible.

   Uses repos file: `$NAME$-not-released.<ros-distro>.repos`

1. Semi-binary builds - against released core ROS packages (main and testing), but the immediate dependencies are pulled from source.
   Shows that local build with dependencies is possible and if fails there we can expect that after the next package sync we will not be able to build.

   Uses repos file: `$NAME$.repos`

1. Source build - also core ROS packages are build from source. It shows potential issues in the mid future.
