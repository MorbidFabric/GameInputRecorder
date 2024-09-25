#include <windows.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <map>
#include "nlohmann/json.hpp"

#pragma comment(lib, "User32.lib")
#pragma comment(lib, "Kernel32.lib")

using json = nlohmann::json;

bool isRecording = false;

struct InputEvent {
    std::string type;
    int dx;
    int dy;
    std::string key;
    double time;
};

std::vector<InputEvent> inputEvents;

std::string VKeyToPynputKey(int vkey) {
    static std::map<int, std::string> vkey_map = {
        {VK_BACK, "Key.backspace"},
        {VK_TAB, "Key.tab"},
        {VK_RETURN, "Key.enter"},
        {VK_SHIFT, "Key.shift"},
        {VK_CONTROL, "Key.ctrl"},
        {VK_MENU, "Key.alt"},
        {VK_PAUSE, "Key.pause"},
        {VK_CAPITAL, "Key.caps_lock"},
        {VK_ESCAPE, "Key.esc"},
        {VK_SPACE, "Key.space"},
        {VK_PRIOR, "Key.page_up"},
        {VK_NEXT, "Key.page_down"},
        {VK_END, "Key.end"},
        {VK_HOME, "Key.home"},
        {VK_LEFT, "Key.left"},
        {VK_UP, "Key.up"},
        {VK_RIGHT, "Key.right"},
        {VK_DOWN, "Key.down"},
        {VK_INSERT, "Key.insert"},
        {VK_DELETE, "Key.delete"},
        {VK_F1, "Key.f1"},
        {VK_F2, "Key.f2"},
        {VK_F3, "Key.f3"},
        {VK_F4, "Key.f4"},
        {VK_F5, "Key.f5"},
        {VK_F6, "Key.f6"},
        {VK_F7, "Key.f7"},
        {VK_F8, "Key.f8"},
        {VK_F9, "Key.f9"},
        {VK_F10, "Key.f10"},
        {VK_F11, "Key.f11"},
        {VK_F12, "Key.f12"},
        {0x57, "Key.W"}, // W key
        {0x41, "Key.A"}, // A key
        {0x53, "Key.S"}, // S key
        {0x44, "Key.D"}, // D key
        // Add more mappings as needed
    };

    auto it = vkey_map.find(vkey);
    if (it != vkey_map.end()) {
        return it->second;
    } else {
        return "Key.unknown";
    }
}

void ProcessRawInput(LPARAM lParam) {
    if (!isRecording) return;

    UINT dwSize;
    GetRawInputData((HRAWINPUT)lParam, RID_INPUT, NULL, &dwSize, sizeof(RAWINPUTHEADER));
    LPBYTE lpb = new BYTE[dwSize];
    if (lpb == NULL) {
        return;
    }

    if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, lpb, &dwSize, sizeof(RAWINPUTHEADER)) != dwSize) {
        std::cerr << "GetRawInputData does not return correct size!" << std::endl;
    }

    RAWINPUT* raw = (RAWINPUT*)lpb;
    auto now = std::chrono::system_clock::now();
    auto now_ms = std::chrono::time_point_cast<std::chrono::milliseconds>(now);
    auto epoch = now_ms.time_since_epoch();
    double timestamp = epoch.count() / 1000.0;

    if (raw->header.dwType == RIM_TYPEKEYBOARD) {
        InputEvent event;
        event.type = (raw->data.keyboard.Flags & RI_KEY_BREAK) ? "key_release" : "key_press";
        event.dx = 0;
        event.dy = 0;
        event.key = VKeyToPynputKey(raw->data.keyboard.VKey);
        event.time = timestamp;
        inputEvents.push_back(event);
    } else if (raw->header.dwType == RIM_TYPEMOUSE) {
        InputEvent event;
        event.type = "move";
        event.dx = raw->data.mouse.lLastX;
        event.dy = raw->data.mouse.lLastY;
        event.key = "";
        event.time = timestamp;
        inputEvents.push_back(event);
    }

    delete[] lpb;
}

void SaveEventsToJson() {
    json j = json::array();
    for (const auto& event : inputEvents) {
        j.push_back({
            {"type", event.type},
            {"dx", event.dx},
            {"dy", event.dy},
            {"key", event.key},
            {"time", event.time}
        });
    }

    std::ofstream file("input_events.json");
    file << j.dump(4);
    file.close();
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    switch (message) {
    case WM_INPUT:
        ProcessRawInput(lParam);
        break;
    case WM_KEYDOWN:
        if (wParam == VK_F6) {
            isRecording = !isRecording;
            std::cout << (isRecording ? "Recording started" : "Recording stopped") << std::endl;
            if (!isRecording) {
                SaveEventsToJson();
            }
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

int main() {
    HINSTANCE hInstance = GetModuleHandle(NULL);
    WNDCLASSEXW wc = { 0 };
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = L"RawInputClass";
    RegisterClassExW(&wc);

    HWND hWnd = CreateWindowW(L"RawInputClass", L"Raw Input", WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 640, 480, NULL, NULL, hInstance, NULL);

    RAWINPUTDEVICE rid[2];
    rid[0].usUsagePage = 0x01; // Generic desktop controls
    rid[0].usUsage = 0x02;     // Mouse
    rid[0].dwFlags = RIDEV_INPUTSINK;
    rid[0].hwndTarget = hWnd;  // Set to hWnd for global input

    rid[1].usUsagePage = 0x01; // Generic desktop controls
    rid[1].usUsage = 0x06;     // Keyboard
    rid[1].dwFlags = RIDEV_INPUTSINK;
    rid[1].hwndTarget = hWnd;  // Set to hWnd for global input

    if (!RegisterRawInputDevices(rid, 2, sizeof(rid[0]))) {
        DWORD error = GetLastError();
        std::cerr << "Failed to register raw input devices. Error code: " << error << std::endl;
        return -1;
    }

    ShowWindow(hWnd, SW_SHOWDEFAULT);
    UpdateWindow(hWnd);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}