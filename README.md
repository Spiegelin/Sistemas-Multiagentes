# How to install and run the project
## Install the requirements for the project
#### Python:
1. Clone the repository to your local machine:
```bash
git clone https://github.com/spiegelin/Sistemas-Multiagentes
```

2. Install the requirements inside `requirements.txt`:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file inside the repository:
```bash
code .env
```

4. Inside the `.env` file, copy the absolute path to the file located at `/Sistemas-Multiagentes/Evidencia_2/ComputationalVision/Model-training/runs/detect/train/weights/best.pt`:
```bash
LOCAL_PATH='ABSOLUTE_PATH'
```

## Usage Python
1. Navigate to the directory */Evidencia_2*:
```bash
cd /Evidencia_2
```
2. Navigate to the directory */Server*:
```bash
cd /Server
```

3. Run the **python** script `Server.py`:
```bash
python Server.py
```

4. Navigate to the directory */ComputationalVision*:
```bash
cd ..
cd /ComputationalVision
```

5. In a new shell, run the **python** script `serverModel.py`:
```bash
python serverModel.py
```

## Usage Unity
1. Download the Unity Package from drive:
```
https://drive.google.com/file/d/19xrx4dFMwaLayRydp6XHng7yyBpzHgZg/view?usp=drive_link
```
2. Create a *Universal Render Pipeline 3D Project.*

3. Import the Unity Package into the project.

4. Open the *Construction Site* scene.

5. Run the simulation.