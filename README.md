# ROS 2 projekt a Kognitív robotika tárgyra (BMEGEMINMKR)
A feladat a Budapesti Műszaki és Gazdaságtudományi Egyetem mechatronika mérnöki MSc képzés Kognitív robotika (BMEGEMINMKR) tantárgyához készült.

Készítette:
- Docsa Bence
- Horváth Ákos
- Kincses Tamás Leó
- Nagy Bertalan

# Tartalomjegyzék
- [Feladatleírás](#feladatleírás)
- [Előkövetelmények](#előkövetelmények)

# Feladatleírás
A projekt megvalósítása során a következő követelményeket kellett teljesíteni:
- Vonalkövetés és színfelismerés neurális hálóval
- Saját vizualizációs node-ban megmutatni a robot által bejárt utat és a vonal színét az út során
- A robot viselkedjen eltérően a különböző színű vonalak esetén

# Előkövetelmények
- Ubuntu 24.04
    - A projekt elkészítése során WSL 2 segítségével használtuk
- [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/index.html)
    - [Telepítési útmutató](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
        - A Desktop Install-t javasoljuk, mert az tartalmazza az RViz-t is
- [RViz](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/RViz/RViz-Main.html)
- [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/getstarted/)
    - [Telepítési útmutató](https://gazebosim.org/docs/harmonic/install_ubuntu/)
    - Szükséges a [Gazebo ROS integráció](https://docs.ros.org/en/jazzy/p/ros_gz/) telepítése:
        ```bash
        sudo apt install ros-jazzy-ros-gz
        ```
- A projekt során [Turtlebot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)-at használunk `burger` konfigurációban
    - Az alábbi csomagok segítségével biztosított a kompatibilitás:
        ```bash
        git clone -b ros2 https://github.com/MOGI-ROS/turtlebot3_msgs
        git clone -b mogi-ros2 https://github.com/MOGI-ROS/turtlebot3
        git clone -b new_gazebo https://github.com/MOGI-ROS/turtlebot3_simulations
        ```
- [Dynamixel SDK](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)
    ```bash
    sudo apt install ros-dynamixel-sdk
    ```
    vagy
    ```bash
    git clone -b humble-devel https://github.com/MOGI-ROS/DynamixelSDK/
    ```