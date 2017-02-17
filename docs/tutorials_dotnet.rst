.. _tutorial_dotnet:

===========================================
Load a 32-bit .NET library in 64-bit Python
===========================================

This example shows how to access a 32-bit .NET library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.dotnet32.DotNet32` is the 32-bit server and
:class:`~msl.examples.loadlib.dotnet64.DotNet64` is the 64-bit client.

.. note::
   The `JetBrains dotPeek <https://www.jetbrains.com/decompiler/>`_ program can be used
   to reliably decompile any .NET assembly into the equivalent C# source code. For example,
   **peeking** inside the **dotnet_lib32.dll** library, that the
   :class:`~msl.examples.loadlib.dotnet32.DotNet32` class is a wrapper around, gives

   .. image:: _static/dotpeek_spelnetlib.png

The following shows that the 32-bit **dotnet_lib32.dll** library cannot be loaded in a
64-bit Python interpreter:

.. code-block:: python

   >>> import msl.loadlib
   >>> msl.loadlib.IS_PYTHON_64BIT
   True
   >>> dn = msl.loadlib.LoadLibrary('./msl/examples/loadlib/dotnet_lib32', 'net')
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "D:\code\git\msl-loadlib\msl\loadlib\load_library.py", line 69, in __init__
       self._net = clr.System.Reflection.Assembly.LoadFile(self._path)
   System.BadImageFormatException: Could not load file or assembly 'dotnet_lib32.dll' or one of its dependencies.  is not a valid Win32 application. (Exception from HRESULT: 0x800700C1)
      at System.Reflection.RuntimeAssembly.nLoadFile(String path, Evidence evidence)
      at System.Reflection.Assembly.LoadFile(String path)

Instead, create a :class:`~msl.examples.loadlib.dotnet64.DotNet64` client to communicate
with the 32-bit **dotnet_lib32.dll** library:

.. code-block:: python

   >>> from msl.examples.loadlib import DotNet64
   >>> dn = DotNet64()
   >>> dn
   DotNet64 object at 0x1d4ee95cda0 hosting dotnet_lib32.dll on http://127.0.0.1:11051
   >>> dn.lib32_path
   'D:\\code\\git\\msl-loadlib\\msl\\examples\\loadlib\\dotnet_lib32.dll'

Get the .NET module name, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_module_name`:

.. code-block:: python

   >>> dn.get_module_name()
   'SpelNetLib'

Get the names of the classes in the ``SpelNetLib`` module, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_class_names`:

.. code-block:: python

   >>> dn.get_class_names()
   ['SpelNetLib.SPELVideo', 'SpelNetLib.SpelControllerInfo', 'SpelNetLib.SpelEventArgs', 'SpelNetLib.SpelPoint', 'SpelNetLib.Spel', 'SpelNetLib.Spel+EventReceivedEventHandler', 'SpelNetLib.SpelException', 'SpelNetLib.SpelAxis', 'SpelNetLib.SpelBaseAlignment', 'SpelNetLib.SpelDialogs', 'SpelNetLib.SpelIOLabelTypes', 'SpelNetLib.SpelWindows', 'SpelNetLib.SpelEvents', 'SpelNetLib.SpelHand', 'SpelNetLib.SpelElbow', 'SpelNetLib.SpelOperationMode', 'SpelNetLib.SpelRobotPosType', 'SpelNetLib.SpelRobotType', 'SpelNetLib.SpelTaskState', 'SpelNetLib.SpelTaskType', 'SpelNetLib.SpelWrist', 'SpelNetLib.SpelVisionProps']

Get the names of the functions that are available in the ``SpelNetLib.Spel`` class, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_class_functions`:

.. code-block:: python

   >>> dn.get_class_functions('Spel')
   ['Abort', 'Accel', 'AccelR', 'AccelS', 'Agl', 'Arc', 'Arch', 'Arm', 'ArmClr', 'ArmDef', 'ArmSet', 'AsyncMode', 'AtHome', 'Atan', 'Atan2', 'AxisLocked', 'BGo', 'BMove', 'BTst', 'Base', 'Box', 'BoxClr', 'BoxDef', 'BuildProject', 'CU', 'CV', 'CVMove', 'CW', 'CX', 'CY', 'CZ', 'Call', 'ClearPoints', 'CommandInCycle', 'Connect', 'Continue', 'CtReset', 'Ctr', 'Curve', 'DegToRad', 'Delay', 'DisableMsgDispatch', 'Disconnect', 'Dispose', 'ECP', 'ECPClr', 'ECPDef', 'ECPSet', 'EStopOn', 'EnableEvent', 'Equals', 'ErrorCode', 'ErrorOn', 'EventReceived', 'EventReceivedEventHandler', 'ExecuteCommand', 'Finalize', 'Fine', 'GetAccel', 'GetArm', 'GetControllerInfo', 'GetECP', 'GetErrorMessage', 'GetHashCode', 'GetIODef', 'GetLimZ', 'GetPoint', 'GetRealTorque', 'GetRobotPos', 'GetSpeed', 'GetTool', 'GetType', 'GetVar', 'Go', 'Halt', 'Here', 'HideWindow', 'Home', 'Homeset', 'Hordr', 'Hour', 'In', 'InBCD', 'InW', 'Initialize', 'InsideBox', 'InsidePlane', 'JRange', 'JS', 'JTran', 'Jump', 'Jump3', 'Jump3CP', 'LimZ', 'LoadPoints', 'Local', 'LocalClr', 'LocalDef', 'MCal', 'MCalComplete', 'Mcordr', 'MemIn', 'MemInW', 'MemOff', 'MemOn', 'MemOut', 'MemOutW', 'MemSw', 'MemberwiseClone', 'MotorsOn', 'Move', 'NoProjectSync', 'Off', 'On', 'OpBCD', 'OperationMode', 'Oport', 'Out', 'OutW', 'Overloads', 'PAgl', 'PDef', 'PDel', 'PTPBoost', 'PTPBoostOK', 'PTran', 'Pallet', 'ParentWindowHandle', 'Pause', 'PauseOn', 'Plane', 'PlaneClr', 'PlaneDef', 'Pls', 'PowerHigh', 'Project', 'ProjectBuildComplete', 'Pulse', 'Quit', 'RadToDeg', 'RebuildProject', 'ReferenceEquals', 'Reset', 'ResetAbort', 'ResetAbortEnabled', 'Resume', 'RobotModel', 'RobotType', 'RunDialog', 'SFree', 'SLock', 'SafetyOn', 'SavePoints', 'Sense', 'ServerOutOfProcess', 'SetIODef', 'SetPoint', 'SetVar', 'ShowWindow', 'Speed', 'SpeedR', 'SpeedS', 'SpelVideoControl', 'Start', 'Stat', 'Stop', 'Sw', 'TGo', 'TLClr', 'TLDef', 'TLSet', 'TMove', 'TW', 'TargetOK', 'TaskState', 'TasksExecuting', 'TeachPoint', 'Till', 'TillOn', 'ToString', 'Tool', 'TrapStop', 'VGet', 'VGetCameraXYU', 'VGetExtrema', 'VGetModelWin', 'VGetPixelXYU', 'VGetRobotXYU', 'VGetSearchWin', 'VRun', 'VSet', 'VSetSearchWin', 'Version', 'WaitCommandComplete', 'WaitMem', 'WaitSw', 'WaitTaskDone', 'WarningCode', 'WarningOn', 'Weight', 'XYLim', 'XYLimClr', 'XYLimDef', 'Xqt', 'add_EventReceived', 'get_AsyncMode', 'get_CommandInCycle', 'get_DisableMsgDispatch', 'get_EStopOn', 'get_ErrorCode', 'get_ErrorOn', 'get_MotorsOn', 'get_NoProjectSync', 'get_OperationMode', 'get_ParentWindowHandle', 'get_PauseOn', 'get_PowerHigh', 'get_Project', 'get_ProjectBuildComplete', 'get_ResetAbortEnabled', 'get_RobotModel', 'get_RobotType', 'get_SafetyOn', 'get_ServerOutOfProcess', 'get_SpelVideoControl', 'get_Version', 'get_WarningCode', 'get_WarningOn', 'raise_EventReceived', 'remove_EventReceived', 'set_AsyncMode', 'set_DisableMsgDispatch', 'set_MotorsOn', 'set_NoProjectSync', 'set_OperationMode', 'set_ParentWindowHandle', 'set_PowerHigh', 'set_Project', 'set_ResetAbortEnabled', 'set_ServerOutOfProcess', 'set_SpelVideoControl']

Get the names of the functions that are available in the ``SpelNetLib.SpelAxis`` class, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_class_functions`:

.. code-block:: python

   >>> dn.get_class_functions('SpelAxis')
   ['CompareTo', 'Equals', 'Finalize', 'Format', 'GetHashCode', 'GetName', 'GetNames', 'GetType', 'GetTypeCode', 'GetUnderlyingType', 'GetValues', 'HasFlag', 'IsDefined', 'MemberwiseClone', 'Overloads', 'Parse', 'R', 'ReferenceEquals', 'S', 'T', 'ToObject', 'ToString', 'TryParse', 'U', 'V', 'W', 'X', 'Y', 'Z', 'value__']

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server`:

.. code-block:: python

   >>> dn.shutdown_server()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server` method to shutdown the server.
