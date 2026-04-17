.. _from-source-installation:

====================
Building from Source
====================

Install NeuroStride-VL directly from source for development or customization.

Development Dependencies
=========================

In addition to runtime dependencies, you'll need:

.. code-block:: bash

   # Development tools
   pip install -U pip setuptools wheel
   pip install -U black isort flake8 mypy pre-commit

   # Testing
   pip install -U pytest pytest-cov pytest-xdist

   # Documentation
   pip install -U sphinx sphinx-rtd-theme myst-parser

Clone Repository
================

.. code-block:: bash

   git clone https://github.com/Chandan118/NeuroStride-VL.git
   cd NeuroStride-VL

Install in Development Mode
============================

This allows you to modify code without reinstalling:

.. code-block:: bash

   pip install -e .

Or with development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Running Tests
=============

.. code-block:: bash

   # Run all tests
   pytest tests/

   # Run specific test file
   pytest tests/unit/test_env.py

   # Run with coverage
   pytest --cov=neurostride tests/

Building Documentation Locally
==============================

.. code-block:: bash

   cd docs
   pip install -r requirements.txt
   make html

Open in browser:

.. code-block:: bash

   open _build/html/index.html  # Mac
   xdg-open _build/html/index.html  # Linux

Pre-commit Hooks
================

Automatically format and lint your code:

.. code-block:: bash

   pre-commit install

Now every ``git commit`` will run:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

Project Structure
=================

For development, understand the structure:

.. code-block:: bash

   neurostride-vl/
   ├── src/neurostride/     # Main Python package
   │   ├── env/            # RL environments
   │   ├── agents/         # RL algorithms
   │   ├── perception/     # Vision-language models
   │   ├── ros2_bridge/    # ROS2 integration
   │   └── models/         # Neural networks
   ├── tests/              # Unit & integration tests
   ├── docs/               # Sphinx documentation
   ├── examples/           # Example scripts
   └── scripts/            # Setup and utility scripts

Adding New Modules
==================

1. Add your module under ``src/neurostride/``
2. Add tests in ``tests/``
3. Update ``setup.py`` if adding new dependencies
4. Document in ``docs/``
5. Add to ``__init__.py`` exports if public API

Common Development Tasks
=========================

Run a single training episode:

.. code-block:: bash

   python3 -m neurostride.train.train_locomotion --timesteps 1000 --algo ppo

Test ROS2 communication:

.. code-block:: bash

   # Terminal 1
   ros2 run neurostride commander_node

   # Terminal 2
   ros2 run neurostride executor_node

Visualize policy:

.. code-block:: bash

   python3 -m neurostride.visualize.realtime_sim --render

Troubleshooting Development
===========================

Import Errors
--------------

Make sure package is installed in editable mode:

.. code-block:: bash

   pip install -e .

Check Python path:

.. code-block:: bash

   python3 -c "import sys; print(sys.path)"

MuJoCo Not Found
-----------------

Set environment variable:

.. code-block:: bash

   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.mujoco/mujoco210/bin

Or add to ``~/.bashrc``.

ROS2 Build Errors
------------------

Clean and rebuild:

.. code-block:: bash

   rm -rf build/ install/ log/
   colcon build --symlink-install

Next Steps
==========

- Read the :doc:`tutorials/quick_start`
- Explore :doc:`architecture/overview`
- Learn about :doc:`training/basics`
