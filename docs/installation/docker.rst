.. _docker-installation:

==========
Docker Setup
==========

Run NeuroStride-VL in isolated Docker containers for easy setup and reproducibility.

Why Docker?
===========

- ✅ **Isolated environment** - No dependency conflicts
- ✅ **Reproducible** - Same environment across machines
- ✅ **Easy cleanup** - Remove everything with one command
- ✅ **Cross-platform** - Works on Mac, Linux, Windows

Prerequisites
=============

- **Docker Desktop** (Mac/Windows) or **Docker Engine** (Linux)
- At least 20GB free disk space
- 8GB+ RAM (16GB recommended)

Install Docker
==============

**Mac**: Download `Docker Desktop <https://www.docker.com/products/docker-desktop>`_

**Linux**:

.. code-block:: bash

   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   # Log out and back in

Quick Start
===========

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/Chandan118/NeuroStride-VL.git
      cd NeuroStride-VL

2. Start development environment:

   .. code-block:: bash

      docker-compose -f docker/docker-compose.dev.yml up

   This builds and starts:
   - Development container with all dependencies
   - X11 forwarding for GUI (optional)
   - Volume mounts for live code reload

3. Enter the container:

   .. code-block:: bash

      docker exec -it neurostride-dev bash

4. Test installation:

   .. code-block:: bash

      python3 -c "import neurostride; print('✅ Ready!')"

Using Docker without docker-compose
====================================

Build image manually:

.. code-block:: bash

   docker build -t neurostride-dev -f docker/Dockerfile.dev .

Run container:

.. code-block:: bash

   docker run -it --rm \
     --name neurostride-dev \
     -v $(pwd):/workspace \
     -w /workspace \
     neurostride-dev bash

GPU Support
===========

For GPU acceleration (required for training):

**NVIDIA Docker** (Linux only):

.. code-block:: bash

   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

   sudo apt update && sudo apt install -y nvidia-container-toolkit

Run with GPU:

.. code-block:: bash

   docker run --gpus all -it neurostride-dev bash

**Mac**: GPU passthrough not available in Docker Desktop. Use native installation for GPU acceleration.

Common Commands
===============

.. code-block:: bash

   # Stop containers
   docker-compose -f docker/docker-compose.dev.yml down

   # Rebuild after changes to Dockerfile
   docker-compose -f docker/docker-compose.dev.yml up --build

   # View logs
   docker-compose -f docker/docker-compose.dev.yml logs -f

   # Remove all containers and images
   docker system prune -a

   # Execute command in running container
   docker exec -it neurostride-dev python3 examples/hello_world.py

Troubleshooting
===============

Permission Denied
-----------------

If you get permission errors:

.. code-block:: bash

   sudo usermod -aG docker $USER
   # Log out and back in

Port Already in Use
--------------------

Change ports in ``docker/docker-compose.dev.yml``:

.. code-block:: yaml

   ports:
     - "8888:8888"  # Change 8888 to available port

Out of Memory
-------------

Increase Docker memory limit in Docker Desktop settings (Mac/Windows):

- Settings → Resources → Memory → Set to 8GB+

Slow I/O
--------

For better file performance on Mac, enable gRPC FUSE in Docker Desktop settings.
