# Guide: Converting to a VST/AU Plugin

Since your project is currently a **React Web App (Frontend)** and a **Python FastAPI (Backend)**, converting it directly to a VST/AU plugin (which are native C++ binaries) requires a specific architectural bridge.

The industry-standard way to do this without rewriting your entire app in C++ is to use **JUCE** with a **WebView**.

## Architecture Overview

1.  **The Plugin Shell (C++/JUCE)**:
    *   This is the actual `.vst3` or `.component` file that you load in your DAW (Ableton, Logic, FL Studio).
    *   It creates a window and hosts a **WebView** (like a mini-browser).
    *   It handles MIDI Output (sending notes to the DAW) and Transport (syncing with DAW tempo).

2.  **The UI (React)**:
    *   Your existing React app runs *inside* this WebView.
    *   Instead of `http://localhost:3000`, the files are bundled into the plugin or served locally.

3.  **The Logic (Python vs C++)**:
    *   *Challenge*: VST plugins cannot easily "run" Python code.
    *   *Solution A (Professional)*: Port your chord generation logic from Python to C++. This is the most performant and stable way.
    *   *Solution B (Prototype)*: Bundle the Python backend as a standalone executable (using PyInstaller) and have the Plugin launch it in the background. The React UI then talks to `localhost:8000` just like it does now.

---

## Step-by-Step Implementation Plan

### Phase 1: Prepare the React App
We need to make your frontend "embeddable".

1.  **Plugin Mode**:
    *   Add a `?mode=plugin` URL parameter or environment variable.
    *   Hide the Header, Footer, and any "page navigation" when in plugin mode. The plugin window is small and focused.
2.  **Dynamic API URL**:
    *   Ensure the API URL isn't hardcoded. It might need to talk to a different port if you spawn a local server.

### Phase 2: Create the JUCE Project
*Prerequisites: Download [JUCE Framework](https://juce.com/) and CMake.*

1.  Create a new **Plug-in** project in Projucer/CMake.
2.  Enable `JUCE_WEB_BROWSER` module.
3.  In `PluginEditor.h`, add a `juce::WebBrowserComponent`.
4.  In `PluginEditor.cpp`:
    ```cpp
    // Example Setup
    webComponent.goToURL("http://localhost:5173"); // For development
    // For release, you would bundle the built React files and use:
    // webComponent.goToURL("file://" + File::getSpecialLocation(File::currentExecutableLocation).getParentDirectory().getChildFile("Resources/index.html").getFullPathName());
    ```

### Phase 3: Communication Bridge (Inter-Process Communication)
Your React app needs to tell the DAW to play notes, rather than playing audio itself via Tone.js.

1.  **From React to C++**:
    *   In C++, bind a function to the WebView:
        ```cpp
        webComponent.withJavascriptFunction("sendMidiToHost", [](const var::Array& args) {
             // Parse JSON MIDI event
             // sendMidiMessage(args[0]); 
        });
        ```
    *   In React, call it:
        ```javascript
        window.sendMidiToHost({ note: 60, velocity: 100, duration: 0.5 });
        ```

2.  **Handling Audio**:
    *   **Disable Tone.js output** in Plugin Mode. The plugin should output *MIDI events*, not audio. The user will put a synth (like Serum or Kontakt) *after* your plugin in the DAW chain.

---

## Recommended Tools

1.  **React-JUCE**: A library that helps integration (though mostly for writing native UI in React syntax).
2.  **Blueprint**: A framework for building JUCE plugin UIs with React.js.
    *   *Highly Recommended*: [Blueprint on GitHub](https://github.com/nick-thompson/blueprint)
    *   It renders React components to native JUCE components, which is much faster than a WebView.

## Immediate Next Steps for You

I will now modify your Frontend code to support **"Plugin Mode"**:
1.  Add a context to detect if running as a plugin.
2.  Hide the main Header/Footer when in plugin mode.
3.  Add a "MIDI Export" button that effectively sends data to the host (mocked for now).
