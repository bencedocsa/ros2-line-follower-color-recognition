[//]: # (Image References)

[image1]: ./assets/turtlebot3_burger.png "Robotmodell"
[image2]: ./assets/track_dark.png "Pálya sötét alapon"
[image3]: ./assets/track_light.png "Pálya világos alapon"

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
- [TurtleBot3](#turtlebot3)
- [Pálya](#pálya)

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
- URDF fájlok megnyitásához:
    ```bash
    sudo apt install ros-jazzy-urdf
    sudo apt install ros-jazzy-urdf-launch
    ```
- A projekt során [TurtleBot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)-at használunk `burger` konfigurációban
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
- [MOGI Trajectory Server](https://github.com/MOGI-ROS/mogi_trajectory_server)
    ```bash
    git clone https://github.com/MOGI-ROS/mogi_trajectory_server
    ```
- Python csomagok:
    - `tensorflow==2.18.0`
    - `imutils`
    - `scikit-learn`
    - `opencv-python==4.11.0.86`
    - `matplotlib`
    - `numpy==1.26.4`

# TurtleBot3
A `burger` konfigurációjú TurtleBot3-at a [turtlebot3_burger.urdf](./line_follower_color_recognition/urdf/turtlebot3_burger.urdf) fájl írja le, szimulációs működését a [turtlebot3_burger/model.sdf](./line_follower_color_recognition/models/turtlebot3_burger/model.sdf) fájl tartalmazza.

A robotmodell megtekinthető RViz-ben a [check_urdf.launch.py](./line_follower_color_recognition/launch/check_urdf.launch.py) launch fájl segítségével:
```bash
ros2 launch line_follower_color_recognition check_urdf.launch.py
```

![alt text][image1]

# Pálya
A projekt során használt pálya egy színes vonalat tartalmaz sötét vagy világos alapon. A vonal három szakaszból áll: piros, zöld és kék. A modellek a [gazebo_models](./line_follower_color_recognition/gazebo_models/) mappában találhatóak.

A pálya megtekinthető és a robottal bejárható a [spawn_robot.launch.py](./line_follower_color_recognition/launch/spawn_robot.launch.py) launch fájl segítségével.

Pálya sötét alapon:
```bash
ros2 launch line_follower_color_recognition spawn_robot.launch.py world:=track_dark.sdf
```

![alt text][image2]

Pálya világos alapon:
```bash
ros2 launch line_follower_color_recognition spawn_robot.launch.py world:=track_light.sdf
```

![alt text][image3]

A neurális háló tanításához szükséges képeket a [save_training_images](./line_follower_color_recognition_py/line_follower_color_recognition_py/save_training_images.py) node segítségével lehet elkészíteni:
```bash
ros2 run line_follower_color_recognition_py save_training_images
```

Ehhez segítségül használható a [line_follower](./line_follower_color_recognition_py/line_follower_color_recognition_py/line_follower.py) node, ami képfeldolgozás segítségével automatikusan végigvezeti a robotot a pályán:
```bash
ros2 run line_follower_color_recognition_py line_follower
```

Robot manuálisan is irányítható:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```