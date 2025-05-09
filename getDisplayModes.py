import ctypes
from ctypes import wintypes

# Constants
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFREQUENCY = 0x00400000

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", wintypes.LONG),
        ("dmPositionY", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

def getDisplayModes():
    """
    Returns a tuple of (width, height, refresh_rate) for every available
    display mode on the primary monitor.
    """
    user32 = ctypes.windll.user32
    EnumDisplaySettings = user32.EnumDisplaySettingsW

    modes = set()
    i = 0
    dm = DEVMODE()
    # dm.dmSize = ctypes.sizeof(dm)
    # print(f"dm.dmSize: {dm.dmSize}")

    while EnumDisplaySettings(None, i, ctypes.byref(dm)):
        # Only add valid modes with non-zero width, height, and refresh rate
        if (dm.dmFields & (DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQUENCY)) and \
           dm.dmPelsWidth > 0 and dm.dmPelsHeight > 0 and dm.dmDisplayFrequency > 0:
            modes.add((dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency))
        i += 1

    # Return a sorted tuple for consistency
    return tuple(sorted(modes))

# def findResolutionIndices(modes, target_resolution):
#     """
#     Find all indices in the modes tuple that match the target resolution.
    
#     Args:
#         modes: Tuple of (width, height, refresh_rate) tuples
#         target_resolution: Tuple of (width, height)
        
#     Returns:
#         List of indices where the resolution matches
#     """
#     indices = []
#     for i, (width, height, _) in enumerate(modes):
#         if (width, height) == target_resolution:
#             indices.append(i)
#     return indices

# def findHighestRefreshRateIndex(modes, target_resolution):
#     """
#     Find the index in modes with the target resolution that has the highest refresh rate.
    
#     Args:
#         modes: Tuple of (width, height, refresh_rate) tuples
#         target_resolution: Tuple of (width, height)
        
#     Returns:
#         Index of the mode with the highest refresh rate, or None if resolution not found
#     """
#     indices = findResolutionIndices(modes, target_resolution)
    
#     if not indices:
#         return None
    
#     # Find the index with highest refresh rate
#     highest_idx = indices[0]
#     highest_rate = modes[highest_idx][2]
    
#     for idx in indices[1:]:
#         if modes[idx][2] > highest_rate:
#             highest_rate = modes[idx][2]
#             highest_idx = idx
    
#     return highest_idx

# Example usage
if __name__ == "__main__":
    modes = getDisplayModes()
    print(f"Found {len(modes)} display modes:")
    # for w, h, freq in modes:
        # print(f"{w}x{h} @ {freq}Hz")
        
    resolution = (1920, 1080)

    # Check if the resolution is in the list of modes
    # indices = findResolutionIndices(modes, resolution)
    indices = []
    for i, (width, height, _) in enumerate(modes):
        if (width, height) == resolution:
            indices.append(i)
    if len(indices) > 0:
        print(f"\nResolution {resolution[0]}x{resolution[1]} found at indices: {indices}")
        print("Available refresh rates:")
        for idx in indices:
            print(f"  {modes[idx][2]} Hz")
            
        # Find the index with the highest refresh rate
        # highest_idx = findHighestRefreshRateIndex(modes, resolution)
        highest_idx = indices[0]
        highest_rate = modes[highest_idx][2]
        
        for idx in indices[1:]:
            if modes[idx][2] > highest_rate:
                highest_rate = modes[idx][2]
                highest_idx = idx
        print(f"\nHighest refresh rate for {resolution[0]}x{resolution[1]}: {modes[highest_idx][2]} Hz (index {highest_idx})")
        print(f"Mode details: r_mode {highest_idx} {modes[highest_idx]}")
    else:
        print(f"\nResolution {resolution[0]}x{resolution[1]} not available")