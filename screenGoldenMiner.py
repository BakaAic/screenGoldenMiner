import ctypes
try:
    import struct, commctrl, win32gui, win32con, win32api
except:
    import pip
    pip.main(['install', 'pywin32'])
    import struct, commctrl, win32gui, win32con, win32api
import platform
from tkinter import *
from tkinter import messagebox
try:
    import PIL as _
except:
    import pip
    pip.main(['install', 'pillow'])
    from PIL import ImageTk
else:
    from PIL import ImageTk
import random
import time
from base64 import b64decode
import pickle
import math

class LVITEMW(ctypes.Structure):
    _fields_ = [
        ('mask', ctypes.c_uint32),
        ('iItem', ctypes.c_int32),
        ('iSubItem', ctypes.c_int32),
        ('state', ctypes.c_uint32),
        ('stateMask', ctypes.c_uint32),
        ('pszText', ctypes.c_uint64),
        ('cchTextMax', ctypes.c_int32),
        ('iImage', ctypes.c_int32),
        ('lParam', ctypes.c_uint64), # On 32 bit should be c_long
        ('iIndent',ctypes.c_int32),
        ('iGroupId', ctypes.c_int32),
        ('cColumns', ctypes.c_uint32),
        ('puColumns', ctypes.c_uint64),
        ('piColFmt', ctypes.c_int64),
        ('iGroup', ctypes.c_int32),
    ]
    
class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]

class ICONCONTROL:
    def __init__(self):
        self.handle_desktop = self.getDesktopHandle()
        self.icons_info = self.getIconsInfo()
        self.oraginal_icons = self.icons_info.copy()
        self.NowIcons = self.icons_info.copy()
        self.recoveryState=False

    def updateIconsInfo(self):
        self.icons_info = self.getIconsInfo()
        
    def updateNowIcons(self):
        self.NowIcons = self.getIconsInfo()
    
    def getDesktopHandle(self):
        # Get the desktop handle
        dthwnd=0
        while True:
            if platform.version().split('.')[0]=='10':
                dthwnd = win32gui.FindWindowEx(0,dthwnd, 'WorkerW',None)
            else:
                dthwnd = win32gui.FindWindowEx(0,dthwnd, 'Program Manager',None)
            ukhwnd = win32gui.FindWindowEx(dthwnd,0, 'SHELLDLL_DefView', None)    
            slvhwnd = win32gui.FindWindowEx(ukhwnd,0, 'SysListView32', None)
            if dthwnd and ukhwnd and slvhwnd:
                break
        return slvhwnd    
        
    def getIconsInfo(self):
        # Get the icons info
        pid = ctypes.create_string_buffer(4)
        p_pid = ctypes.c_void_p(ctypes.addressof(pid))
        ctypes.windll.user32.GetWindowThreadProcessId(self.handle_desktop, p_pid)
        hProcHnd = ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, struct.unpack("i",pid)[0])
        pBuffertxt = ctypes.windll.kernel32.VirtualAllocEx(hProcHnd, 0, 4096, win32con.MEM_RESERVE|win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
        copied = ctypes.create_string_buffer(4)
        p_copied = ctypes.c_void_p(ctypes.addressof(copied))
        lvitem = LVITEMW()
        lvitem.mask = ctypes.c_uint32(commctrl.LVIF_TEXT)
        lvitem.pszText = ctypes.c_uint64(pBuffertxt)
        lvitem.cchTextMax = ctypes.c_int32(4096)
        lvitem.iSubItem = ctypes.c_int32(0)
        pLVI = ctypes.windll.kernel32.VirtualAllocEx(hProcHnd, 0, 4096, win32con.MEM_RESERVE| win32con.MEM_COMMIT,  win32con.PAGE_READWRITE)
        win32api.SetLastError(0)
        ctypes.windll.kernel32.WriteProcessMemory(hProcHnd, pLVI, ctypes.c_void_p(ctypes.addressof(lvitem)), ctypes.sizeof(lvitem), p_copied)
        num_items = win32gui.SendMessage(self.handle_desktop, commctrl.LVM_GETITEMCOUNT)
        p = POINT()
        pBufferpnt = ctypes.windll.kernel32.VirtualAllocEx(hProcHnd, 0, ctypes.sizeof(p), win32con.MEM_RESERVE|win32con.MEM_COMMIT, win32con.PAGE_READWRITE)
        icons = {}
        for i in range(num_items):
            win32gui.SendMessage(self.handle_desktop, commctrl.LVM_GETITEMTEXT, i, pLVI)
            target_bufftxt = ctypes.create_string_buffer(4096)
            ctypes.windll.kernel32.ReadProcessMemory(hProcHnd, pBuffertxt, ctypes.c_void_p(ctypes.addressof(target_bufftxt)), 4096, p_copied)
            key = target_bufftxt.value
            win32api.SendMessage(self.handle_desktop, commctrl.LVM_GETITEMPOSITION, i, pBufferpnt)
            p = POINT()
            ctypes.windll.kernel32.ReadProcessMemory(hProcHnd, pBufferpnt, ctypes.c_void_p(ctypes.addressof(p)), ctypes.sizeof(p), p_copied)
            icons[key] = (i,[p.x,p.y])
        ctypes.windll.kernel32.VirtualFreeEx(hProcHnd, pLVI, 0, win32con.MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(hProcHnd, pBuffertxt, 0, win32con.MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(hProcHnd, pBufferpnt, 0, win32con.MEM_RELEASE)
        win32api.CloseHandle(hProcHnd)
        #icons = {key: (i, [p.x, p.y])}
        return icons

    def moveIcon(self,icon_name,pos,recovery=False):
        # Move the icon
        if recovery:
            if icon_name in self.oraginal_icons:
                win32gui.SendMessage(self.handle_desktop, commctrl.LVM_SETITEMPOSITION, self.NowIcons[icon_name][0], win32api.MAKELONG(int(round(pos[0],0)),int(round(pos[1],0))))
                return True
            else:
                return False
        else:
            if icon_name in self.icons_info:
                win32gui.SendMessage(self.handle_desktop, commctrl.LVM_SETITEMPOSITION, self.NowIcons[icon_name][0], win32api.MAKELONG(int(round(pos[0],0)),int(round(pos[1],0))))
                return True
            else:
                return False
            
    def point_to_long(self,pos):
        ret = (pos[1] * 0x10000) + (pos[0] & 0xFFFF)
        return ret
        
    def getIconPos(self,icon_name):
        # Get the icon pos
        if icon_name in self.icons_info:
            return self.icons_info[icon_name][1]
        else:
            return False
    def getIconsName(self):
        # Get the icons name
        return self.icons_info.keys()

    def recoveryIconsPos(self):
        # Recovery the icons pos
        self.updateNowIcons()
        for icon in self.oraginal_icons:
            self.moveIcon(icon,self.oraginal_icons[icon][1],recovery=True)
        return True

class Game():
    author="Aikko"
    def __init__(self):
        self.ICON=ICONCONTROL()
        self.screen_width = None
        self.screen_height = None
        self.temp_icon_pos = {}
        #===========Angle===========#
        self.angleMin=10
        self.angleMax=170
        self.angle=10
        self.angleForward=1
        #--------#
        self.totalAngle=abs(self.angleMax-self.angleMin)
        self.halfAngle=self.totalAngle//2
        self.midAngle=self.angleMin+self.halfAngle
        #--------#
        self.speedLevel=3
        #===========Line===========#
        self.lineMin=50
        self.line=self.lineMin
        self.lineOutSpeed=10
        self.lineBackSpeed=3
        #===========Trigger===========#
        self.TriggerPos=(-1,-1)
        self.HookOrder=False
        #===========Point===========#
        self.score=0
        
    def __call__(self):
        self.Tips()
        self.main()
        
    def basePicData(self):
        _data=b'gASVQf8AAAAAAACMElBJTC5QbmdJbWFnZVBsdWdpbpSMDFBuZ0ltYWdlRmlsZZSTlCmBlF2UKH2UKIwDZHBplEdAUgCTdLxqf0\
                dAUgCTdLxqf4aUjBFYTUw6Y29tLmFkb2JlLnhtcJRoAIwEaVRYdJSTlFgHBwAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU\
                0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYm\
                UgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxucz\
                pyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm\
                91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYm\
                UuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUm\
                VmIyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1sbnM6ZG\
                M9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcG\
                hvdG9zaG9wLzEuMC8iIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcDpDcmVhdGVEYX\
                RlPSIyMDIyLTEyLTI5VDE2OjU5OjM0KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMi0xMi0yOVQxNzoyMTozNCswODowMCIgeG\
                1wOk1ldGFkYXRhRGF0ZT0iMjAyMi0xMi0yOVQxNzoyMTozNCswODowMCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDoxNThkZG\
                U1MS1iNDVlLWY5NDctOGE1Zi00YTVkYzUwOTUyYjciIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6MzYxMEU2QTk4NzI5MTFFRE\
                I4MDFGNTE3MjQ2Njk2NjQiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDozNjEwRTZBOTg3MjkxMUVEQjgwMUY1MT\
                cyNDY2OTY2NCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiPiA8eG1wTU06RGVyaXZlZEZyb2\
                0gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozNjEwRTZBNjg3MjkxMUVEQjgwMUY1MTcyNDY2OTY2NCIgc3RSZWY6ZG9jdW1lbn\
                RJRD0ieG1wLmRpZDozNjEwRTZBNzg3MjkxMUVEQjgwMUY1MTcyNDY2OTY2NCIvPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+ID\
                xyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpmMjE1OWRlOC0xMDY5LWFjNDctYm\
                NlZC0yZDAwOGU4NDI5MjQiIHN0RXZ0OndoZW49IjIwMjItMTItMjlUMTc6MjE6MzIrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbn\
                Q9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE5IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdG\
                lvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6MTU4ZGRlNTEtYjQ1ZS1mOTQ3LThhNWYtNGE1ZGM1MDk1MmI3Ii\
                BzdEV2dDp3aGVuPSIyMDIyLTEyLTI5VDE3OjIxOjM0KzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3\
                AgQ0MgMjAxOSAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDxwaG90b3\
                Nob3A6RG9jdW1lbnRBbmNlc3RvcnM+IDxyZGY6QmFnPiA8cmRmOmxpPnhtcC5kaWQ6MzYxMEU2QTk4NzI5MTFFREI4MDFGNTE3Mj\
                Q2Njk2NjQ8L3JkZjpsaT4gPC9yZGY6QmFnPiA8L3Bob3Rvc2hvcDpEb2N1bWVudEFuY2VzdG9ycz4gPC9yZGY6RGVzY3JpcHRpb2\
                4+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz6UhZSBlH2UKIwEbGFuZ5SMAJSMBHRrZXmUaBB1Yn\
                WMBFJHQkGUS3JLi4aUTkKY9wAA////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wArK5kAJy\
                uYACcsmQAnK5gAKCuaACksmwAlK5sAKC2aACgsmQAoLJkAKC2aACgsmQApLZoA7eD9AO3g/QDs3/wA7N/8AOvf/ADt3vsA7d76AO\
                zd+QDr3fgA69z4AOvc9wDq3PYA6tv2AOvb9QDq2vMA6tnzAOvY8gDq2PEA6NjwAOnX7wDp1+4A6NbtAP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AM/AygDbydYA4M7cAN/O2wDezdkA3czYANzM1gDcy9UA3MrUANvK0wDbydIA28jQANrI0ADax8\
                4A2sbNANnGzQDZxcwA2cTLANnEywDZw8oA2MPKANjDygDYwskA2MHIACUrlgAoK5YAJSqXACcrmAAmK5cAJSqXACcrmgAoK5oAJi\
                qZACcqmQAoK5oAJiqZACgplwAqK5gAKiuYACsrmQAqK5gAKiuYACgplwApKpcAKSqXACgqlwAsK5UALi2XACgplwAkJ5QAJCaQAC\
                cokgAuLZcANzOYADc0mAA0MpcALCyVACIkiQAxLYgATECJAH1aiQDGizMA56cuAOGkGgDjowcA////AP///wD///8A////AP///w\
                AqK5kAKyyZACsrmQApLJsAKSybACksmwApLJsAKCyZACgsmQAoLZoAKCyZACgsmQAmK5gA6+D+AOzg/QDu3/0A7N/8AO3f+wDt3/\
                oA7N76AOzd+QDs3fkA6934AOrb9wDq2/YA69v1AOva9ADr2vQA69nyAOnZ8QDo2PEA6tjwAOnX7wDo1u4A6NbtAMOzuQB3YlX/l4\
                aK/5+Nkv+aio7/lYKE/499ff+LeHf/h3Nu/4JuZ/99aWH/fGhj/3toZ/94aGz/r5ycAMKvtADVw8oA3MrTANvJ0wDbydIA2sjQAN\
                vHzwDax84A2sfOANnGzQDZxcwA2cTLANjEywDZw8oA2MPKANjCyQDYwskA18LIACYslwAlK5YAKSyWACkslgAlKpcAJSuXACcsmA\
                AnKpoAJiqZACYqmQAmKpgAJiqYACYpmAAmKpkAKSqXACormAAqKpgAKiqYACormAAqK5gAKiqYACkqlwAqKpgAKiuYACormQAqK5\
                kAKSqXAC4tlwAqKpUAKCmTACoqlQAuLZcALi2XADQynAArK5YAHR+GADozigB6UEUAp24AANWXAADwsB8A////AP///wD///8A//\
                //AP///wAoK5oAKSybACgrmwApLJsAKSybACksmwAnK5oAJiuYACgsmQAoLJkAKCyZACotlwApLJcA6+D+AOzf/QDs4P0A7d/7AO\
                3e+wDt3voA7N35AOzd+QDr3fgA69z4AOrc9wDr2/UA69v1AOva9ADq2fMA6dnyAOnZ8QDq2PEA6dfvAOfX7gDo1u0A6NbtAOfU7A\
                CsmZoAgnBx/8a10f/OvNX/0b7X/9G/1//Rvtf/0r/X/9TB2P/Pu8//wq+9/7Wlrv+nlpv/lYKD/4Rva/92YVX/dWFa/6CLhQDBrr\
                MA28jPANrHzgDax84A2cbNANnFzADZxcwA2cTLANjEywDZw8oA2MPKANjCyQDYwskA2MHIACgtlQAlK5UAJCuVACkslgAlKpcAJS\
                uXACcsmQAmKpkAJiqZACUpmAAmKpkAJiqZACYqmQAmKpkAJiqZACYqmQAmKpkAKiuZACormAAqKpgAKiuYACormQApKpcAKiqYAC\
                wrlQAuLZcAMS+YADIwmQAtLJYAKiqVACoqlQAsK5UAKCmTADUymwA0MZcAKSmPADgyjABLNnQAZzsMAJFdAAC7gwAA////AP///w\
                D///8A////AP///wApLJsAKSybACksmwApLJsAKSybACksmwAkK5oAJyyZACgsmQAoLJkAKC2aACkslgAmLJcA7OD9AO7g/ADs3/\
                wA7d/7AO3e+wDt3voA7N75AOzd+QDr3PgA6tz3AOzb9gDq2/YA69v1AOva9ADq2vMA5tPqAM6/yQCxnqIAnYmEAJN+dgCSfnUAk3\
                52AJJ9dACPenAAemNQAINuaP/QvNH/4M7l/+bU6v/j0ef/4c3j/+PP4//gzuH/4M7h/+DN3//byNj/1sTU/9O/0f/Nucr/tKSq/5\
                WChP95Y1b/dWBS/6yXlQDPu8EA2sbNANnFzADZxMsA2cXMANjEywDZw8oA2MPJANjCyQDYwskA18HIACktlQAoLJQAJiyXACUrlg\
                AoK5UAJSqXACcsmAAnKpkAJyuaACgrmgAnK5oAJiqZACYpmAAmKpkAJyuaACgrmgAoK5oAJyuaACcrmgAnKpkAKiqYACormAAqKp\
                gAKSqXACkqmAAqKpgAKyyZAC0tmgAsLJoALCyaACormAAtLJYALSyWACsrlgAvLZMAKiuTAC4tkgAuLZIAJieMACcmiQBWSZUA//\
                //AP///wD///8A////AP///wApLJsAKSybACksmwApLJsAKSybACUrmwAoLJkAJiuYACgsmQAoLJkAKSyXACUrlgApLZUA7t/9AO\
                7f/ADs3/wA7d/7AO3e+wDt3voA7N76AOvd+ADr3PgA69z3AOrb9gDs2/UA6dfwAMq6wgCnlZQAkn51AJaCewCCcnf/lIKS/6COpf\
                +jk6r/p5Op/6SSpv+ejZ7/kYGH/4Z0c//Nuc3/3szi/+TS5v/gzuL/4Mzg/9/O3f/fzN7/4M7f/+DO3//cy9r/2cjV/9rJ1v/Zx9\
                T/2MjS/9TDz//Lucj/rZyi/4Zzcf92YVj/noiBAMizuQDZxcwA2cTLANjEywDZw8oA2MLJANfCyQDYwcgA2MHIACkulAArLZQAKS\
                2VACYslgApLJYAJyuYACYrmAAqK5gAJyuaACgrmgAoK5oAJyuaACcqmQAoK5oAJyuaACgrmgAnK5oAKCuaACcqmQAnK5oAJyqZAC\
                crmgAqK5gALCyZAC4umwArLJkAKiuYACoqmAArLJkAKyuZAC4tlwAtLJYALy+XACsrlAAsLpkAKy2YACgokwAwLpQAMS+VACcliQ\
                BLPYMA////AP///wD///8A////AP///wApLJsAKSybACksmwApLJsAJyuaACcrmAAmK5gAJyyZACkslgAqLJcAJiyXACktlQAnLJ\
                QA7N/9AOzf/ADs3/wA7d/7AOze+gDs3voA7N35AOzd+ADr3PgA69z3AOjY8QCwnqEAjHZrAHxoYP+Sg4j/vqrA/9bF4P/dzeb/3M\
                zl/9rK4v/ayuL/2srh/9nJ3//byd//2sjd/9jH2//cyt7/4c/i/+DO4f/ezNz/4M7e/93M2f/cy9n/3MrZ/9zL2P/bytf/28rX/9\
                3M2f/dzNr/3czZ/9nI1P/XxdL/1MLQ/9C9zP+/rrr/koCE/3hjXf+jjYcA077EANjEywDYw8oA2MPJANjByADXwcgA18DHACovlQ\
                AoLZMAKi6WACotlgAmK5YAKiyXACcrmAAoLJkAJyuaACcrmgAmKpkAJiqZACgrmgAnK5oAJyqZACgrmgAoK5oAJyuaACcrmgAoK5\
                oAJyqZACcrmgAnK5oAJyqZACksmwArK5kAKiqYACormAAqKpgAKiuYACoqmAAuLZcALSyWAC0slgAuL5oAMzGbADAumAAqKpUAJi\
                eRAC4skgA0MZIA////AP///wD///8A////AP///wAoK5oAKCuaACksmwAqLJwAJyyZACcsmQAnLJgAKSyXACUrlgApLZUAKC2VAC\
                stkwAlLJUA7N/9AOzf/ADt3/sA7d/7AO3e+wDs3vkA7N75AOzd+ADgz+QAq5mbAH5oVwB/bGv/rZuv/9DC3P/ezub/5dPr/+fX7v\
                /q2vD/69nw/+rY7v/n1+3/6Nbs/+jW7P/m1Or/49Lm/+PS5f/j0eL/4c/g/9/O3//ezNz/3s3b/9zM2P/by9f/2crU/9rL1f/byt\
                b/2svU/9nJ0//YyNH/2crT/9bG0P/ZytT/3MvU/9jH0f/XxdD/0b/J/7uosf+Db23/j3hrANG8wgDYw8oA2MLJANfCyADXwcgA18\
                DHACkulAAoLZMAJi2WACotlgAoLJQAKSyWACotlwAnLJkAJSqXACYqmQAmKpkAJiqZACcrmgAoK5oAJiqZACYqmQAmKpgAJiqZAC\
                YqmQAmKpkAJiqZACYqmQAmKpkAJiqZACQolwAlKZgAKiuYACssmQArK5kAKiuZACormQAqK5gAKCmXACsrlgAoK5UAKiqUAC8umA\
                AsK5UAJyiSAC4tlwAoKZMA////AP///wD///8A////AP///wApLJsAKSybACksmwApLJsAKCyZACgsmQAqLZcAJSuWACktlQApLZ\
                UAKy2TACgulAAqLpEA7eD9AOzf/ADt3/sA7d76AO3e+gDs3fkA5tTtALKipgCUf3cAeWpw/6mcu//TxuT/4tPu/+jX8f/p2fH/7N\
                rz/+nZ8P/q2e7/6dfu/+nX7f/o1uv/59Xq/+XU6P/l0+b/49Hk/+PR4v/gz97/383d/97O2v/fz9v/3MzY/9zM2P/czdj/2szV/9\
                rL1P/aytL/2cnR/9nJ0P/ZyND/2MjP/9jI0P/ZyNH/2cfP/9jG0P/ayND/2MfP/9TCy//Kt8H/k3+A/3dhWf/FsLQA2MLJANfByA\
                DYwcgA18DHACsvlgAoLZMAKS2VACotlgApLZUAKSyWACotlwAnLJgAKSqXACgplwAmKpgAJyqZACgrmgAnK5oAKCuaACcrmgAoK5\
                oAJiqZACYqmQAmKpkAJiqZACcrmgAnK5oAJiqZACYqmQAmKpgAKiuYACoqmAAqK5gAKiqYACormAApKpcAKiuZACormQApLJYAKS\
                yWACwumQAtL5kALCuVACwrlQArK5UA////AP///wD///8A////AP///wApLJsAKSybACgrmwAoLZoAKCyZACgsmQArLZgAJiyWAC\
                cslAAnLJQAKC2TACswlgApLpQA7OD9AOzf/ADr3/sA7d77AO3e+gDq3PYAl4R+AJ+MiQCbjaj/x7zb/+LR7//o1/P/6Nn0/+vb9P\
                /q2vH/59Xu/+PT6v/m1Or/49Pp/+LQ5v/i0eX/4dDj/+HP4v/i0OP/4tHi/9/O3//ezdz/3c3Z/97O2v/dzdn/283W/9zN1f/dzd\
                X/28vT/9jJ0f/ay9P/2cnR/9jIz//ZyM//2MfP/9jHz//Yxs7/1sTM/9jGzf/Xw8r/2sfO/9nGzf/Uwcn/0L3G/6SRlv92YFf/0L\
                nAANfByADXwcgA18DHAC4xlQAsL5MAKy+SACwvkwArLZMAKS2VACkslgAnLJkAJyyYACkqlwApKpcAKCuaACgrmgAnK5oAKCuaAC\
                grmgAnK5oAJyuaACcrmgAoK5oAKCuaACcqmQAnK5oAJiqZACcrmgAmKpkAJiqZACYqmQAmKpkAJyuaACoqmAAqK5gAKiuYACsrmQ\
                ArLJkAKiuZACormAApKpcAKyuVAC0slgAqKpQA////AP///wD///8A////AP///wApLJsAKSybACYsmwAoLJkAJyyZACYrmAAqLZ\
                cAJiyXACgslAAmK5MAKC2TACovlQAuMZUA7uD8AO7f/ADr3/sA7d76AOHP5QCTf3cAhXR5/7isz//Yyej/4dTx/+va9//r3Pf/6t\
                r0/+bY8P/l1ez/5tbt/+LS6P/j0ef/4tHl/+PR5v/j0eX/4dDi/+HP4v/i0OH/4NDd/97P3P/ez9v/3c3Z/9zO1//bzNX/28zV/9\
                3N1f/ay9T/2crS/9zN1P/aydD/2crQ/9rJz//ZyM7/28rQ/9rJz//ZyM7/2MfN/9jGzP/Ww8r/1sLJ/9bCyf/Xwsr/1MDH/8+8xf\
                +ahor/c11S/8y1uwDXwMcA18DHACwwkgAtMJQALC+TACotkgArLZMAKS2VACkslgApLJYAJSqXACkqlwAoKZcAKiqYACcqmQAnK5\
                oAJyuaACgrmgAnK5oAJyuaACgrmgAnK5oAKCuaACgrmgAoK5oAKCuaACgrmgAnK5oAJyuaACgrmgAnK5oAJyqZACormAAqK5gAKi\
                qYACsrmQAqK5gAKiuYACkqlwApKpgAKyuWACsrlgAqK5QA////AP///wD///8A////AP///wAoK5sAKSybACgrmwAoLJkAJyuYAC\
                UqlwAoK5UAJSuWACktlQAqLpYAKC2TACsukgApLZAA7N/8AOzf/ADt3vsA59bwAJyIgwCEdn7/wLLW/9zN6//m1/X/7dz4/+vb9f\
                /m2PL/5tbv/+bW7f/k1ev/4tLo/+XT6v/l1Oj/4tPm/+HS5P/i0eT/5NPk/+PS4//i0eD/4dHe/+DQ3P/g0d3/3tDa/97Q2f/dzt\
                f/28vT/9rL0//by9H/28vR/9vL0f/Yx83/3czS/97N0//dzNL/2snP/9rIzv/byM7/2cfN/9jGzP/Zxcz/1cLI/9fDyf/Xwcj/1s\
                HI/9TAx//MuMH/lYCD/3plYf/SusEA18DHACcrigAqL5AALC+TACoukQAsLpQAKy2TACorlAAmKZQAJSuXACgplwAoKpcAKiqYAC\
                ormAAoK5oAJyuaACcrmgAnK5oAJyuaACcrmgAnKpkAKCuaACgrmgAnKpkAJyuaACgrmgAoK5oAJyuaACksmwAoK5oAKSybACcrmg\
                AmKpkAKiuZACormAAqK5gAKiuYACormAAqK5gAKSqXAC4tlwAwMZwA////AP///wD///8A////AP///wAoK5oAJyuaACgrmgAnLJ\
                kAJiuYACkslwApLJYAJiyXACktlQAnLJQAJy2SACkskQAsMZIA7N/9AO3f+wDo2PAAkn52AIh3ff/MwOT/5NT1/+XW9P/o2fX/59\
                j0/+XX8P/m1e//5dXu/+XV7f/j0+r/4tLp/+XU6f/i0+f/5NPn/+PS5f/i0OP/49Hi/+DQ3v/fz93/3s/c/9zO2P/bzdf/2cvU/9\
                nK0//XydD/08XM/9HCyP/UxMr/08PJ/9HBx//Swcf/1cXL/9jHzf/ayM7/2cjO/9nHzf/Xxcv/18TK/9jFy//bx83/1sLI/9XAx/\
                /Wwcj/18HI/9O/xv/RvMT/zbjB/4t2d/+TfG8A1r/GACsujQArMJEALTCUACsvlQArLpcAKi2WACotlwArLZgAKSyWACkqlwApKp\
                cAKSqXACkqlwAqK5gAKyuZACcrmgAnK5oAJyuaACcrmgAlKZgAJiqZACYqmAAmKpkAKCuaACcrmgAnK5oAKCuaACgrmgAoK5oAJy\
                uaACgrmgAmKpkAJyuaACcrmgAqKpgAKiqYACoqmAAqKpgAKiuZACormAAmKJUA////AP///wD///8A////AP///wAoK5sAKCuaAC\
                QqmgAlKpcAJCqWACkslgAsLpgAKC2YACYrkgAiKJAAJCuQACoukQAnLY4A7N/8AOPV7gCdiYUAiXl+/9TD5v/k1/j/5dj3/+fX9v\
                /k1fH/4tTv/+TW7//l1e7/49Xu/+TU7f/j0+v/4tLo/+bV6v/k0+f/39Di/+LS4//l1OX/49Ph/9zN2f/SxM//y77G/8O2vf+0pq\
                v/o5WZ/5eJiv+XiIb/mYuG/5uKgf+PfnT/i3pu/49+cv+RgHb/emtf/21eVP91Zl7/iXlz/52Oi/+0o6X/yre8/9bDyf/Zxcv/1s\
                LJ/9K+xf/Uv8X/1b/F/9W/xv/WwMf/073F/8Grs/95Y1z/qJGNADIyiAAsLosAKCyQACgtkwArLZMAKy2TACorlAApLJcAKSyXAC\
                csmAApKpcAKSqXACkqlwAqK5kAKiqYACormQAoK5oAJyuaACcrmgAmKpkAJiqZACYqmQAmKpkAJyuaACcrmgAmKpkAJiqYACcrmg\
                AoK5oAJiqZACYqmQAmKpgAJyuaACoqmAAqK5gAKiuYACoqmAAqK5gAKyyZACotmwAmKJUA////AP///wD///8A////AP///wApLJ\
                sAKSybACcrmAAnLJkAJiuXACkslgArLpgAJiyXACYrkwAlKpIAJCuQACgsjwAuMJAA7N/8AK+eogCCcHX/0sXs/+bW+P/l1vb/5t\
                f1/+TV8//n1vP/5tfy/+XX8f/k1O3/5dXt/+TW7v/j0+r/49To/+PR5v/h0uT/5tTn/+LS4P/Xx9X/x7nD/6+hpf+qm5j/oI+F/6\
                iWhv+zoY//tqOP/7Keif+9qZH/x7Ka/8Oslf+3oIr/q5V//7Kchf+3oIr/vaaQ/7Wehf+oknr/q5V//6CLdv+Remn/gWxe/5F8df\
                +6paj/0b3D/9nEyv/Vv8T/073D/9a/xv/XwMf/1L3E/8y2vf+plZz/iHBgAEpAdwA2M4cALC6PAC0wlAAuMZUALS6SACkrkgAqK5\
                QAKi2XACoslwAqK5gAKSqXACormAAqK5gAKiuYACoqmAAoK5oAJyuaACcrmgAnK5oAJyqZACYpmAAnK5oAJyqaACcrmgAmKpgAKC\
                uaACcrmgAnK5oAJiqZACYqmAAmKpkAKCuaACgrmgAqKpgAKiuYACkqlwAqK5kAKiuYACssmQAoLZoA////AP///wD///8A////AP\
                ///wApLJsAKSybACcrmAAmK5gAKCyZACkslgApLJYAJiyXACktlQArLZMAJiyRACYqjgApLIgA2sjdAJF9dADDsdL/6tr7/+3f+/\
                /o2fn/5db1/+TU8//o2fX/5dbx/+PS7P/h0+v/4NLq/+HR6f/g0Ob/4tHl/+PU5v/l1OX/3c3d/7+yt/+WiIj/iHlu/6eVh/+5pp\
                T/yLSg/97Jsv/jzrX/7dS7/+zSt//x17n/7tO0//TcvP//7s7///XV///lxf/t0rH/4sen/+LIpf/kyqn/2L6e/860lP+/poj/p4\
                90/4x3YP+Icl//o42G/8u1uv/Ywcf/1sDG/9O9w//TvMP/1L3E/9W/xv/Js7v/hnB1/1hIUAAyMIQALi6OACwvkwAxMJQAKy2TAC\
                gpkQAmKZQAKCuVACotlwAuLZcAKiuZACgplwAoKZcAKSqXACormAAqK5kAJyuaACcqmQAoK5oAKCuaACgrmgAoK5oAJyuaACcqmQ\
                AnKpkAJyuaACksmwAnK5oAJyuaACYqmAAmKpgAJyuaACgrmgAnK5oAKSqXACgqlwAnLJkAJyuYACcrmAAkKZYA////AP///wD///\
                8A////AP///wAnKpkAKCuaACcsmQAmK5gAJyuYACoslwAnLZcAJyyXACgslAApK5IAJSyRACktkAApLIgAoY6MAJiIkv/g0vb/6N\
                j5/+LV9f/azer/08Pd/9PB2f/OvdH/yLbH/8Szwf/Mu87/zr7U/9fI3f/n1er/5tXq/+XU5v/Vx9L/l4mK/31vaP+jk4j/zbiq/+\
                zWxv/p0bv/7dS9/+zTuv/nzbL/8de5/+3Ss//s0rP/8te2/+DGpf/Hro7/uqB//8eriv//5ML/9ti2/+3Prf/01rP/7M6s/+LFo/\
                /kx6f/3sKk/8qvlP/ApI3/iXBc/5Z+cv/KtLf/17/E/9a/xf/Wv8X/1b3D/9W9xP/Ks7r/l4OK/2JNSgBIPXAAODSFAC0shQAtLI\
                UANjKLADEwkAAvLpMAKiuTACgrlQAuLZcALy6YAC4tlwApKpcAKyuZACwsmgAqK5gAKCuaACcqmQAnK5oAJyuaACcrmgAoK5oAJy\
                uaACcrmgAnKpkAKCuaACgrmgAnK5oAJyqZACYqmQAmKpkAJyqZACcrmgAnK5oAJyuaACcrmgAqK5kAKiqYACormAAoKpcA////AP\
                ///wD///8A////AP///wApLJsAKSybACYsmwAoLZoAKCyZACgrlQApLJYAKS2VACYrkwAoK5EAKy6SACgujwBGQYwAc1xHAMm+5v\
                /ZzfP/1Mbq/72w0v+Cb2r/b1hC/25XQP9wWEEAcVpDAHJbRQBvV0H/ppej/9TF2v/p1+3/y77E/4NuXv+HeHD/f29l/8q1p//jzb\
                v/9t7K//Lawv/r07v/69O7/+bNtP/jyq//6s6x/+LGqP/u0rP/xquQ/2lTO/8oFwD/GQQA/z8sF/+9o4n/6s2v/+zPr//sz63/6c\
                uq/+7Rrv/kx6f/6Mqs/+XGqf/WtZf/0rGT/6SFaf+ojof/y7O2/9vCxv/Uu77/z7a4/9C0tv/Fq67/t5ub/3FVSv9wV03/a0xwAE\
                k7dgAmI3cAKyqIADAvjwA1MpMALi2SACsrlAAuLZcALy6YAC8umAAtLJYAKiuZACwsmgArLJkAKCuaACcqmQAoK5oAJyuaACksmw\
                ApLJsAKSybACcrmgAnKpkAKCuaACcqmgAoK5oAJiqZACYqmQAmKpkAJyuaACcrmgAoK5oAKCuaACcqmgAnKpkAKCuaACkqlwApKp\
                cA////AP///wD///8A////AP///wAoK5oAKCubACksmwApLZoAKCyZACkslwApLJYAJiyWACgslAApK5EAKi6RACgtjgBfUX8Agm\
                5t/8/F6v+9tNz/i3uT/4x4bQCei4cAwrO6ANPDzgDayNkAr52gAHhkWv+unKz/z7/V/9TD2P+fjY7/b1dA/25XP/96aV7/p5OD/+\
                HKtv/p0bn/2r+n/+DEqv/lya//68+y/+zQtP/qzrL/6s2v/+jMrv/32rz/pIlr/ygUAP8nFAD/Zk42/0UwGv9BKxT/qo5y/+vMrv\
                /z07P/7M6q/+3Pqf/nx6L/3b6b/9+/mv/mw5//8Mym/9Syjf+Qclr/wKin/9C2u//FqKT/sI+A/7qTfP/Al3z/to9z/8KbhP+Ial\
                j/dVtV/29Rgv9EOn8ALSuFACwsjQA1MpMALi2SACwslQAqLJcAKi2XAC4tlwAuLZcALSyWACormAAqK5kAKCuaACcrmgAoK5oAJy\
                uaACksmwAoK5oAKCubACgrmgAnK5oAJyuaACcrmgAoK5oAJiqZACYqmQAmKpkAKCuaACgrmgAnK5oAJyuaACcrmgAnK5oAKCuaAC\
                cqmQAnLJgA////AP///wD///8A////AP///wApLJsAKSybACcrmgAnLJkAJyyZACotlwApLJYAJiyWACktlQAqLJIAKCyQACosjg\
                BoUWkAl4eP/7Go1v+Dc4v/jXhuAMu7xQDr3fcA7Nz2AOvb9QDezOAAeGRZ/7ejuf/Rwdn/0sDY/4t5df9vV0D/dF1HAFNFRf+SgY\
                T/wKuj/6SMev+ReWP/vKKI//TYvv/z173/58uv/+rOsv/sz7H/7dCw/+vOrv/73bv/uZ17/3lfQP+8nnz///DM/+TDof80HQD/TD\
                MX/72ff//uzq3/8dCt/+zMqf/ryqX/4sKd/+G+mf/kwZv/5cGZ/9u4kP+8nH3/rJCC/6qMfv+ng2z/uJJ3/9mxk//50bD/9c2u//\
                HIrP/ftqD/h2ta/3JZSf9wUnkARDuDACQkggArLI8AMjCRAC8ukwAsLJUAKSyWACotlwApLJYALi2XACormAArK5kAKiuYACcqmQ\
                AnK5oAJyuaACcrmgAoK5oAJyuaACcrmgAoK5oAJyuaACcqmQAnK5oAJiqZACcrmgAnK5oAKCuaACgrmgAoK5oAJyuaACcqmQAnK5\
                oAKCuaACcqmQAoLJkA////AP///wD///8A////AP///wApLJsAKSybACcrmgAnK5gAJyyZACwumQAqLZcAJiyXACotlgApLZUAJy\
                qQACwujwD///8Al4uu/8a2vQCPenEA3cndAOvd+ADr3PcA7Nz2AOrb9gCZhX8AjX2C/9DB3f/Qwdz/koGF/3BZQgB2X0oAzb7IAE\
                g+Wv+aipj/sJ6f/1tGOv9hSTX/r5N7/+7Qtv/y1rv/4seq/+3Qsv/tzrH/7s6v/+XGp//vz67/9tWw//zYsf/zz6b/886m//PPp/\
                /Oq4T/MhsA/3lcOv/31rP//9/A/+bGo//ryqX/6MWh/+TAm//dupP/3LaQ/+zGof/ctJD/m3lc/4hlRv/asZD//tS1///Xuv//2b\
                7//dW9//3Uu///3MX/47mn/35jT/9yWUb/cFN+AD41fgAzL4wANDGSAC8ukwArLJQALCyVACotlwApLJYALCuVAC0slgApKpgAKi\
                uYACcqmQAnK5oAJyqZACcrmgAoK5oAJyqZACcrmgAnK5oAKCuaACcrmgAnK5oAKCuaACcqmgAnK5oAJyuaACgrmgAnK5oAJyuaAC\
                cqmQApLJsAKSybACgrmgApLJsA////AP///wD///8A////AP///wAoK5sAKSybACcrmgAmK5gAKCyZACwumQAqLZcAKSyXACgtlQ\
                AoLZUAJimPAC4wiAD///8A////AP///wDRwc0A6934AOvd+ADs2/cA6tz3AOHP5ABzXU3/yrnX/8u81/+LeXv/b1dAAHZfSwDk0O\
                YA6NbuAEY3Sv+gkZb/t6Od/xsEAP9tVT3/48Sn//7ewP/oyaz/6cmq//HSsv/szKv/8dGy/+3Kqv/px6X/+dWx//PPqf/00Kj/8c\
                yi/+vHnf//3rb/PiQA/z8nBv/Proz//+K//+bGof/syaL/58Ob/+TAmf/gvJP/4LqR//nRqP/sxZz/n3tW/4djQf/nwJ3//9i4//\
                /bwP//38f//dbC//fPuP//18D//NK7/96zoP92XEf/cFdR/006dwA0L4IANTGPAC4tkgAsLJUAMS+VAC4tlwAtLJYALCuVACwrlQ\
                AoKZcAJyuaACcrmgAoK5oAKCuaACgrmgAnKpkAJyuaACcqmQAnKpkAJyuaACgrmgAnK5oAJyqZACcqmQAnK5oAJyuaACgrmgAoK5\
                oAKCuaACgrmgApLJsAKSybACksmwApLJsA////AP///wD///8A////AP///wApLJsAKCuaACcrmgAmK5gAJyyZACotlwAqLZcAKi\
                yXACYslwApLZUAKSuRAC8xhABURGMAfWdVANDAzAD///8A6934AOvc+ADs2/YA6tv2ALSjpwCKeX7/zL3d/5SEiv95Yk8ApZKQAO\
                TS6ADn1+4A6NbuAFNCVP+kkZT/o4uB/y0YBP+afWL//+LC/+zMq//qyKj/7syr/+3KqP/syqf/88+r//LPq//30av/68Wd//LMpf\
                /wyaD/9M2k///guP//4bn/pIJd/5RzT//kwJv/99Ot//DMpP/vyqL/4r6X/+O9lP/kvpX/5L2T/+bAlf/btY3/l3NO/41rSv/jup\
                z/9Myx///Wu///1rn/4bic/7uSdf+1inD/2q6W/+/Drv+xjYX/cFhG/3FPdQBMP4QAMy+NADIwkQAxL5QALCyVACwslQAsLJUAKS\
                yWACwrlQAqK5gAKiqYACcqmQAoK5oAJyuaACcqmQAoK5oAJyuaACgrmgAnK5oAJyuaACgrmgAoK5oAJyuaACcrmgAnK5oAKCuaAC\
                crmgAnKpkAKCuaACcqmQAnK5oAJyuaACgrmwAnKpkA////AP///wD///8A////AP///wApLJsAJyuaACgrmgAnK5gAJyyYACcrmA\
                ApLJYAKiyXACUrlgAoLZUAJyyUACoskgArL5IA7N76AOze+QDr3fgA6934AOrc9wDq3PcA////AP///wCunLP/s6rN/3BZRv+lk5\
                IA6tjwAOnX7wDo1u4ARDhb/3Nfcf98Z2r/RTAn/1hAL/+3mYH/89Gy//LPrf/ryab/78yp//DNq//vzKj/8cum/+3HoP/1zqf/99\
                Cm/+zFnP/yy6L/3LSM/86ngP/sw5r/472U/+3Fm//xyqH/8cqi//HMo//uyaH/4LuU/+K9lv/kvpX/68Sb/+W/lv/Io33/i2hI/4\
                BfQP/Bm4D/9cyx//jPsv/nvp7/xpx8/6p/YP+hd1n/1qmN//rNtv/mu7P/dVxN/2pSUwBENnQAPjaJADo0jgA0MZIAMS+UADEvlA\
                AsLJUALCyVACkslgAqLZcAKiqYACormQAoK5oAKCuaACcrmgAnK5oAKCuaACcqmQAoK5oAKCuaACcqmQAnK5oAKSybACgrmgAnKp\
                kAJyqZACcrmgAnK5oAJyuaACgrmgAnK5oAJyuaACksmwAoK5oA////AP///wD///8A////AP///wAoK5sAKCuaACksmwAoLJkAJy\
                uYACYrmAAqLZcAKi2XACgrlgAkK5UAKS2VACoskgAqLpEA7d76AO3e+gDs3fgA6934AOvc9wD///8A////AP///wC1qsj/clxN/4\
                RuYADn1e0A6NjwAObV3ADl1dwAVUNZ/5eChv+WfHH/XEMu/5J0Xv/lwqj/+dS2//DLp//tyqb/8M2o//PNqv/xy6b/9s+o//HLo/\
                /uxp//9Muk//7Uq//Gn3b/iWZA/31bNv+xi2T/78ab//7YrP/yyqD/8Mmf//HKov/sxp7/6MKb/+jBm//gupT/47yU/+C6kf+3kn\
                L/n31f/4tqTf+Mak3/68Kj///Yuf/luZj/solo/6d8W/+tg2P/2auM/+/Bpf/ovK3/iWtk/2xUQABFNnMAPjaGADcyjAA2MpAAND\
                GSAC8ukwAvLpMALCyVACwslQAqLZcAKi2XACcrmAAnK5gAKiuYACormQAnK5oAKCuaACcrmgAoK5oAJyuaACcrmgAoK5oAKSybAC\
                ksmwAnK5oAKCuaACcrmgAnK5oAKCuaACgrmgAnK5oAJyuaACgrmgAoK5oA////AP///wD///8A////AP///wApLJsAKSybACksmw\
                AnLJkAJyyZACUqlwAlKpcAJSuXACotlwAqLZcAJSuVACcslAAoLJQA7N76AOze+QDr3fgA69z4AOzc9gDs3PYA////AP///wD///\
                8Ad2BNAOnZ8QDq2PEA6tjwAObV3ADl1NwAZk9m/5R8ev/MrZX/1rOW/9+7mf/0zqv/99Gt//HLpf/zzKf/9c+p/+3HoP/yy6T/+d\
                Kr//XOpP/rxZz//NOq//nRqP+adlH/RysL/1Q3Gf94Vzb/2bSL//fQpf/yy6H/8Mmf/+7Hn//rxJz/6cKa/+jCmf/euJD/7MWc/9\
                u0iv+ohV//spF1/6uNdv+Mak//4biZ//3SsP/PpIL/qn9d/6N5Wv+1imr/1aeG/+69oP/gs6D/kG9s/21VQABDNnsAOzSIADYxiw\
                AxLpAAMS+UAC8ulAAxL5QALy6TACwtlQAqLZcAKi2XACoslwAmK5cAJyyZACcsmAAnLJgAKCyZACYrmAAnK5gAJyyZACcsmAAoK5\
                oAJyqZACcrmgAoK5oAJyqaACgrmgAoK5sAKCubACgrmwAnK5oAKCuaACcqmQAnK5oA////AP///wD///8A////AP///wAnK5oAJy\
                uaACcrmgAnK5gAJyyYACUqlwAnLJkAJyuYACYrmAApLJYAKi2XACYslwAoLJQAJyyTACgulAAnLJIAKi2SACswkQAsL48AKzCNAP\
                ///wD///8ARz5lAC0xigAxM4oAKi6DAObV3ADl1NsAalVo/5l/ff/gvqj//9y+///auv/qw6L/27eU/+jDov/tx6L/9M6p//LJov\
                /1zKX/7sWd//HIoP/2zab/+9Kr/+O9lv+HZUX/PyUH/0wwFP9ZPB//zKeB//rSqf/xyqH/7sef/+3Gn//qw5z/58Ga/+rEnf/mv5\
                f/9c6k/8eie/+MbEv/wKON/8WqmP+NbFL/1a2P/+3Dof+7kW7/soZk/9Smhf/SpYL/4rSQ//nIqP/tvqj/jm1i/2xUPwBON3QAQD\
                aDADYwhwA6M44AOjSTADkzkQA1MJIAMzCSADEvlQAsLJUAKi2XAC0slgApKpcAKiuYACormQAqKpgAKiuYACYrmAAmK5gAJyyZAC\
                YrmAAqK5gAJyuaACgrmgAoK5oAJyuaACcqmQAnKpkAKSybACcrmgAnKpkAKCuaACcrmgAoK5oA////AP///wD///8A////AP///w\
                AnK5oAKSybACksmwAoK5oAJyuYACcrmAAnK5gAJiuYACUrlwAlKpcAKSyWACkslgAmLJcAKS2VACgslAArLZQAJiySACkskQAoLo\
                8A////AP///wAqLIUALzGJADIzjwAqL4gAJy2FAOXV3ADl1dwAYU5a/6yPjP/cuKH/6MKl/+3HrP+/nYD/kHBV/6yJcP/qwqL//d\
                Wx//XMp//2zab/8cef//bNpP/60ar/+M+o/8ymgv97Wjz/RywS/1s+I/9DKQz/wp58//vUrv/xy6P/6sOc/+vEnf/rxJ3/6sOc/+\
                nCm//gu5T/99Gr/8WhfP+MbU7/x6+g/9G6r/+Zd1z/x6KE/+O5mP/EmXb/2aqH//jLqP//1a///Mun//XDof/xv6j/impZ/2xTQQ\
                BRM2MARjd7AEY5hABDOY0AQDiTADgzkgA2MZAANTCSADMwkgAsLJUAMi+VAC4tlwAtLJYAKiuYACormAAqKpgAKiuZACormAAmK5\
                gAJyyYACcsmQAnLJkAKiuYACcqmQAnK5oAJyuaACcqmQAnK5oAKCuaACgrmgAnKpkAJyqZACcqmQAoK5oA////AP///wD///8A//\
                //AP///wApLJsAKSybACcrmgAnK5oAKCuaACQrmgAnLJkAJyyYACYrlwAlK5cAJyyZACcrmAAqLZcAKSyWACktlQAoK5UALC6UAC\
                svkgAtLpAALS+PACovjAAsL4oALDGNACswjQApLYcAKi2IAObV3ADl1NwAbFdg/7SVj//kv6X//NW6//DKsf+CZE3/LBMA/1Q5Jv\
                /SrI7//ta0/+7Gof/yyaL/9Mui//bNpP/vx6D/88qk/9Wujf+Makz/YUMq/3ZYPP9PNRv/xKF///rTrf/xyqP/6sSd/+rDnP/qxJ\
                3/6sSd/+bBm//fu5X/6MSg/7uYdv+XeV7/yLSr/9G9tf+ninb/qods/+O5mv/uwqH/8sKg//bJqP/8zqn/+8uk//bEpP/isZz/eV\
                1J/2pRSABZOWoARzmDAEY6iwBAOJMAPTaUADkzkgA2MZAAMy+SADUxlAAwLpUAMS+VADEvlQAuLZcAKiuYACoqmAAqK5gAKiuYAC\
                csmQAnLJkAJiuYACYrmAAnLJkAJyyZACYrmAAnLJkAKCuaACgrmgAnKpoAKCuaACcrmgAnKpkAJyuaACcqmQAnK5oA////AP///w\
                D///8A////AP///wApLJsAKSybACcrmgAnK5oAJyuaACcrmgAoK5oAKCuaACYqmAAnK5oAKiqYACcrmAAmK5gAKi2XACkslgAmLJ\
                cAKi6WAC0vlQAqLpEAKSuMACcrigAvMI0ALTCPACcujQAqL4wALDCNAObV2wDl1NsAalRb/7+flf//2b//8syw/8Ofh/+DY0z/XD\
                8q/3FTP//CnoD/+M+s/+/Gov/yyqP/982l//PJof/txJ7/+tGq/+vDof+XdVf/Vzsh/2dJLv9gRCn/zamH//bQqv/wyaL/5sCZ/+\
                XAmf/pw5z/6cWe/+fEnv/qyaP/1rST/6SEZv+pj3z/zLiw/9XBuf+8pZn/h2hP/8umiv/70bP/8san//bJp//xw53//8+o//nHpf\
                ++kYD/b1ZA/2dNVQBXOG8ASTuFAEU6iwA+N5IARDqTAD82kgA+NZEAOTOSADYxkwA1MZQANjGTADAulAAxL5UALi2XAC4tlwAtLJ\
                YALSyWAC4tlwAuLZcAKSyWACcrmAAnK5gAJyuYACcrmAAmK5gAJyuYACormQAoK5oAJyuaACcqmQAoK5oAKCuaACcqmQAoK5oA//\
                //AP///wD///8A////AP///wAnK5oAKCuaACcrmgAnK5oAJyuaACcqmQAnK5oAJyuaACcrmgAnK5oAJyuaACsrmQAmK5gAJiuYAC\
                otlwAoK5UAJSuWACwvlwAmLJIAJSmNACksjQAtMJAAKi6RAC0vjwAuMo8ALjCMAOXV2wDl1dsAcVpg/8OilP//27//78ir/7aSef\
                +LalD/iGZL/62Kbf/atJH/9Myp/+/Hov/0y6X/9syk//TLov/2zKT//NOs/+a+mv+jf13/Z0gs/3RWOv+efV7/78mm//3WsP/vya\
                L/5MCa/+fCnf/lwZz/4b6Z/9++mv/uzaz/wKKG/5F2XP++qZ//0b21/9bCuv/NuLH/l3xs/41tVv/MpYz/78es//PHpv/zw5v/57\
                eO/8+gfv+NaFL/bVQ+/1k2WABRN3QARDiGAEc6jABFOpIAQTiUAEA3kwA+NZEAPzaSADs0kwA4M5UANzKUADEvlQAxL5UALi2XAC\
                0slgAuLZcALSyWAC4tlwAuLZcAKi2XACkslgAnLJgAJyuYACcrmAAmK5gAJyuYACormAAqKpgAJyuaACgrmgAnK5oAJyuaACcrmg\
                AoK5oA////AP///wD///8A////AP///wAoK5sAKCubACgrmgAnK5oAJyuaACcrmgAnKpoAJyqZACgrmgAnK5oAJyuaACoqmAAnLJ\
                kAJyuYACYrmAAoK5UAJSyWACktlQAqLJIAKCyQACsvkgArL5EALDGSAC8zkAA1NIsANDOGAOXU2wDl1NoAb1Ra/8WklP//273/6s\
                Ok/8Cbe/+rh2b/tY9t/9myjv/yyaL/8Meh//HIpP/0y6T/88uk//LIoP/2zaT/8smg/+7FnP/IoXz/kW9O/3FTNP+aeVn/0q6M/+\
                rFof/mw5//6MSf/+vJpf/qyKX/6cim/+3Orf/ixaj/pIpy/5J9bf/LurP/0r+3/9K/uP/Tvrj/w7Co/4twXv+WdV7/wJyC/8ibef\
                /ClGr/rn9U/6V1Tv+IY0n/akk+AEgrQABdPXcARDiHAEQ5jgBBOJMARzuUAEQ5lgA8NZUAOzSTADs0lAA9NZQAOTOWADkzlwAuLZ\
                cALSyWAC0slgAuLZcALi2XAC0slgAuLZcALi2XACotlwApLJcAJiuYACUqlwAmK5cAJiuYACcrmAAqK5kAKiuYACcrmgAnK5oAKC\
                uaACgrmgAnK5oA////AP///wD///8A////AP///wAnK5oAKCuaACcrmgAnK5oAJyuaACcrmgAoK5oAKCuaACgrmgAoK5oAKCuaAC\
                cqmQAqK5kAJyyYACgsmQArLpgAKi2XACgslAAqLJIAKS6UACoukQAqL5AALjCQAC0xjgAyMYQAPTiBAOXV2wDl1NsAblNW/8mkk/\
                //38L/3bWV/6yGZv/JoHz/7cWe//fOp//1zKX/8Meh//XMpf/1zKb/9Muk//DHnv/0yqL/88mh//LIoP/yyaP/zqeE/39gP/+DZE\
                T/mXhX/7WUcv/An37/za6N/9W3l//StZT/0rWX/82xlf+fiXH/h3Nf/8Gup//Qv7j/1MK8/9C9tv/Sv7n/1L+6/8u2rv+eg3L/eV\
                pE/5pwTP+hdEn/qntM/6Z2TP+RZEP/f1VK/2tJVABeO2sAWDhxAFM5fgBMO4cARjmIAEU5iwBGOYsAQTeNAD81jQBANo4AODKNAD\
                YxkAAxLZAALiyTADEulAAwLpUAMzCWAC8umAAxL5gALy6YAC4tlwApLJYAKi2XACcrmAAmK5cAJiuXACYrmAAmK5gAKiqYACsrmQ\
                AnKpkAJyuaACcqmQAnK5oA////AP///wD///8A////AP///wApLJsAKSybACgrmgAnK5oAJyqZACgrmgAnKpkAKSybACcqmQAnKp\
                kAJiqZACYqmQAmKpkAJiuYACgsmQApLZoAKi2XACktlQArLZMAKC2TACktkAApLJEAKC+TACsvkQAlKYgAOjaAAOXU2wDl1NoAel\
                5f/82pmv/qwaP/sotn/7OMaP/ht5L/+c+p//nPqf/1zKb/8Meh//TLpP/80qv//NKr//TLpP/xyKH/8Mmi//XOp//6067/1LCN/6\
                OCYv+zkXP/o4Vq/450Xf+NdmH/hW9e/4p2Zf+bhnb/kn1u/35tYP95al3/taWf/869uP/Twb3/0L65/9C+uP/Sv7n/0r65/9PAuv\
                /Araf/e1xH/6N7Wv+4i2H/uIhZ/72JWf+0f07/sXpG/6RvOv+RWyj/gk8i/4JNH/+FUCH/fUkd/2w7H/9vQDX/aEBJ/1EwQf9VMF\
                4ARi1pAD0ygAAxLIgANS+PAC4skwAvLZMAMC6UAC4tlwAxL5kALSyWACsrlgAtLJYAKy2XACotlwAoK5UAJiuXACYrmAAnK5gAJy\
                uYACormQAnK5oAJyqZACcrmgAoK5oA////AP///wD///8A////AP///wAnKpkAJyuaACcqmgAnK5oAKCuaACcrmgAoK5oAJyuaAC\
                grmgAnKpkAKCuaACgrmgAnK5oAJyuaACYrmAAmK5gAKSyWACgslAAqLJIAKC2TACYskgAqLZIAKi+UAC0xkgAsLosAPTiAANzK0A\
                Cfhov/gl9L/7SRgf+7lXj/nXdX/82kgv/2zaj//NOu//DIo//zy6b/88ql//PKpv/0y6T/9cyl//bNpv/2zab/8Mmi//XPqv/30K\
                v/1K+N/6uJbP/Lqo3/17+1/821pf+5oY7/mYV0/5uGd/+hjoD/m4p9/6iXjv/BsKz/zb66/9XFwf/Pv7r/0L66/9G+uf/Rv7n/0L\
                63/9PBuf/Fsqz/knRj/6d+Xv+9kGb/wZBg/8mVYf/DjVn/xItW/72FT/+2fUf/woRI/7R3Ov+ucDT/pWgs/5RcIv+JUyP/h1M1/3\
                hLQP9lQ1b/aUBt/2RDf/9OP4kARDmKADw1kAA0L44ANjGTAC8tkwAyL5UALy6YAC0slgAuLZcAKiyXACkslwApLJcAJSuXACYrmA\
                AlK5cAJiuYACUqlwAnKpkAJyuaACYqmQAnK5oA////AP///wD///8A////AP///wAkKpsAJCqbACcrmgAnK5oAKCuaACgrmgAoK5\
                oAKCuaACcrmgAoK5oAKCuaACcrmgAoK5oAJyqZACYqmQAmK5cAKCuVACcskwAqLJIAJy2SACctkgApLZEAJi2RACkujwAqLIkARD\
                t5AKOHdwB3UjD/lHNg/5t6bf+Tb1T/poBh/+vBn///2bX/+9Kv//XMqv/xyab/88uo//XNqP/zyqb/8sql//XMp//zzaf/7Meh//\
                jSrP/40q//1rKT/6KDZ//JqpL/3MjE/9/Nyf/cy8f/28jE/9XEv//Swbz/0sPB/9XHxf/XyMb/1cXD/8+/vP/PwLz/z7+7/9G/uf\
                /Qvrj/zbu1/9K/uf/ItK7/nIN0/5dyUf+zhl3/vo1d/8KOXP/Ci1b/w4pT/8OIUP/FilD/15dZ/9GPUf/KiUr/x4ZF/75+P/+2dz\
                3/rnM+/6lwRP+gakz/l2RN/49fVP9+VV//a0hk/1s/ff9EOYoAPDWQADUwjwAzMJIANDGXADIwlgAuLZcAKCuVACkslgApLJYAKS\
                yXACUqlwAlK5cAJSqXACYrmAAnK5oAJyqZACYqmQAoK5oA////AP///wD///8A////AP///wAoK5oAJyuaACgrmgAnK5oAJyuaAC\
                grmgAnKpkAJyuaACcqmQAoK5oAJyqZACgrmgAoK5oAJyuaACgrmgAnLJkAKiyXACktlQAqLJIAJiySACoukQAnLpIAKC6PACwvjg\
                AsMY0AV0NpAHhTMACJZ07/yrS5/49vZP+Na1X/yKCD//XOr///3Lz/+dS0//TPr//wyar/8Mup//TMqf/1zar/8sqn//HLqP/xy6\
                j/78qm//PQq//00a7/z66O/5N2W//MsZ//3MrG/9rJxv/ZyMb/2MjG/9fHxv/TxcT/1cbE/9XFxP/XyMb/18nH/9XGw//Tw7//0c\
                G9/9C/uv/Qvrj/0b+5/9PBu//LubL/q5OG/5JtTf+xhl3/xJJg/8OOWv/Ejlj/x45V/8aLUf/LjlL/x4hM/8qLTf/Ni0r/yolF/8\
                uJRP/Qjkr/0Y9L/8yKSf/Ni0n/xYdE/79/P/+1eTn/pW41/4xZNf9pSFf/Xz93/0I4jAA4Mo0AOTOSADIwlgAzMJYAKi2XACkslg\
                AqLZcAKSyWACgrlQAlKpcAJiuYACYrmAAnK5oAJyuaACgrmgAnK5oA////AP///wD///8A////AP///wApLJsAJyqZACcrmgAnK5\
                oAJyuaACgrmgAnK5oAKCuaACgrmgAoK5oAJyqZACcqmQAoK5oAJyuaACgrmgAmK5gAKSyXACktlQAmLJIAJyuPACgrkAAqL5AAKC\
                6PACsujgAsLoYAZUY2AHZQLACtk43/2MTK/4ptZ/+UdGD/58Gm//bQtP//4MP//di8/+zIqv/xzKz/8Mys//LNq//yzKv/8Mup/+\
                /KqP/wy6n/8cyq//DOq//vzKz/xKSJ/5F0XP/VvrP/3svI/9bFw//WxsX/18bF/9bHxv/Vxsb/18nH/9PFxP/TxcT/08XD/9PEwv\
                /SxL//0cG+/829uf/NvLf/0L+6/9C/uv/LuLP/t6CV/4xoSv+qgFb/w5Nh/8GNWP/DjFT/x45V/8iMUP/IjFH/xohJ/8mISP/KiE\
                f/yYhC/8uGQv/PjUf/0Y9J/8+NR//Nikj/zY1I/86PSv/PkEv/yYxK/7R6Qf+SYUb/cU5Z/1o/f/9DNn4AOjOKADQwkwAzMJYALz\
                CbACwumQArLZgAKi2XACgrlQAqLZcAJyyYACcsmQAqKpgAJyqZACgrmgAnK5oA////AP///wD///8A////AP///wApLJsAKSybAC\
                crmgAnK5oAJyqZACcrmgAoK5oAJyqaACcrmgAnK5oAKCuaACcrmgAoK5oAKCuaACcrmgAnK5gAKi2XACcslAAnLZMAJCqQACoukQ\
                ArMJEALS+PACwxjgAzM4YAcEkmAHdSMv/Aqan/4MvR/49zbf+Yd2X/+9W9//rWvP//3sP//tq9//DMsP/zzrD/886u//LNq//yza\
                v/8cuq//DLq//wy6z/7Mqp//TSsf/lw6X/spZ8/5+FcP/YxcH/3MrI/9fHxf/Zycj/2srJ/9XGxf/TxcT/1cfG/9THxf/Ux8b/0s\
                XD/9LEwv/TxML/0sK//8+/u//Nvbj/0L+6/869uP/OvLb/w66l/41rTv+mfFX/xZZl/8GNWf/Bi1P/yI5T/8iMUf/IjE7/y4xN/8\
                KCQ//Fg0L/0Y1K/9CMSf/Lh0T/yYhE/8mIR//Ih0r/yIhI/8iJSf/MjUr/0JNR/8eLTv+2fUv/l2hU/3FOW/9eO2r/SDmBADYwiw\
                AtLJMAMTCZACstmAAoK5YAKCuVACkslgApLJcAJiuYACcsmQAoK5oAJyuaACgrmgAnKpkA////AP///wD///8A////AP///wApLJ\
                sAKSybACcrmgAnKpkAKCuaACcqmgAnK5oAKCuaACcqmQAnK5oAKCuaACcrmgAoK5sAKCuaACcqmQAnLJgAKi2XACktlQAmLJIAKC\
                yQACUskAAqLY0ALS6LACovjAA8M3IAb0opAIJhS//Mt7v/48/W/6SIg/+cfW7/8s+3//vYv//72sD/+tm7//jWuf/vza//8s6u//\
                POrv/zzqz/78ur/+/Kqv/uy6v/6cip//DOr//HqY3/nYJq/8awpP/cysf/28nI/9vKyf/VxcT/z8HA/9DCwv/Yysn/1MbG/9THxv\
                /TxsX/08XE/9TFxP/TxcL/0cO//9HBvv/Ovrn/zr25/829uP/RwLr/x7Kp/4hnS/+bckz/xpZl/8SSXP/Ci1T/xItQ/8aLT//Hi0\
                3/z45O/7J0M/+2dDP/yodE/82KR//EgT//wn89/8SEQP/GhUT/yoxL/8iJRv/HiUb/yotG/8uOSv/JjU//uoBK/5VlTv9vSFH/XT\
                11ADgxiAApKY8AMTCZACsrlAAlKZMAKyuUACotlwApLJcAJiuYACcsmQAqK5kAKCuaACcrmgAnK5oA////AP///wD///8A////AP\
                ///wApLJsAJyuaACgrmgAoK5oAJyuaACcrmgAnK5oAKCuaACgrmgAnK5oAJyuaACgrmgAnK5oAKCuaACormAAmK5gAKi2XACktlQ\
                AnLZIAKCuQACYsjAApLIsALi+MACovjAA8M20AcEonAI9yaf/TwMb/48/W/7mgn/+ggnP/2Lej//bWvP//4Mb//t3B//XUt//ty6\
                3/7Mqp/+/NrP/xzKz/7smq/+fFp//uzLD/9ta4/9y9oP+wlHz/n4Z1/9rHw//bysj/1sXE/9vMzP/Nv77/qZyd/7uvr//Xysr/0c\
                TE/9TIx//RxcT/0sXE/9PGxP/Rw8H/0MG+/9HCvv/Ov7r/zby4/828t//Vw73/x7Or/4JhRv+RaUX/yJhn/8+aZf/Fjlf/xYtR/8\
                eLUP/OklT/z49Q/6dqLP+dYCD/snIw/7h3M/+zcy7/tXUw/7d4Nf+/gD7/yotI/8iJSf/Gh0X/x4hG/8mMS//OkVP/wIdT/6dyRv\
                99UD//Z0Jw/zw0hAAoKI4ALy+YACwslQAoKZEAKyuUACgrlQApLJYAJyyYACcsmQApKpcAJyqaACgrmgAnK5oA////AP///wD///\
                8A////AP///wAoK5sAKSybACksmwAoK5oAJyuaACcqmgAnK5oAKCuaACcqmQAnK5oAJyuaACYqmQAmKpgAKCuaACormAAmK5gAKC\
                uVACoskgAqLpEAKzCRAC0vjwAqMJAALDGOAC0yjwA6M28AaEc0AJh+fP/Vwsn/4s3T/9W9vP+pinv/q4t2/+fHrv/+3cH/+Ne8//\
                HStv/y0bT/6cep/+rJqv/uzK3/7syt//LRtP/uz7H/17me/7CVfP+giHL/0r65/9rKyP/Wxsb/1cXF/+DS0P+toKH/Pzo6/4R7e/\
                /RxcX/0MTD/9XIx//RxcT/z8LB/9PFxP/TxcP/08XB/9DBvf/Mvrr/z765/868uP/SwLr/zLiw/4ZlS/+WcU//xpdq/8eTXv/Fjl\
                b/y5FX/8yRVf/Tllr/yYtO/6ZpK/+QVBT/mFsb/6JkJf+lZiT/qWgo/65wLf+4eTr/x4ZH/8+QTf/MjEz/yItJ/8iMTP/KjU//xY\
                lL/7B5R/+VY0H/bUlU/0Y2dgAtKogAMzGWADAvlAArK5EAKiuUACgrlgApLJYAJiuYACUrlwApKpcAJyuaACcqmQAnKpkA////AP\
                ///wD///8A////AP///wAoK5oAKCubACgrmwApLJsAJyqZACcrmgAnK5oAJyuaACgrmgAoK5oAKCuaACcrmgAnK5oAKCuaACormA\
                AnK5gAKSyXACgslAAnLZMAJi2RACsujgAsLo4AKzCNACwxjQA5MmsAaUg1AJ2Egf/dy9L/5NHX/9/L0P+0mI3/k3Vk/6yPef/NrZ\
                X/4sSo/+rMsP/627///N3B//navP/11bj/8NGz/9e6nv+1mX//oIVt/6SMeP/NurT/2cjH/9jIx//YyMj/2crL/8q9vf9waGn/Hx\
                0d/4yDg//UyMj/1MfI/9HFxf/Sxsb/0cXE/9HEw//RxML/0sXC/9DBvv/Mvbn/zr65/869uP/SwLr/zLiv/4lpTf+bdVP/sYRY/5\
                9uOf+ZZi//pnA3/6lzN/+sczf/tno+/51hJf+KTxH/mFsc/7Z1Nf/IhUL/yIdE/8SEQP/Ih0b/yotI/8qLSP/MjUr/yYxI/8mMSv\
                /Ljk//yY1N/7Z/Tf+TYkX/a0lV/0c3dwAwLYsAMzGVAC8ukwAsLJIAKyyUACgrlQApLJYAJiuYACcrmAApKpcAJyuaACksmwAnK5\
                oA////AP///wD///8A////AP///wAnK5oAKSybACgrmwApLJsAKSybACcrmgAoK5oAJyuaACcrmgAnK5oAKCuaACcrmgApLJsAKC\
                uaACsrmQAmK5gAKi2XACktlQAmLJIAKCyQACgujwArLo0AJy6NAC0wigA2MWsAakk1AJ+Gg//i0Nb/5NLY/+LR1v/dyMr/sZaI/5\
                p+bP+kiXX/tZqD/7yji/+8oon/yK2T/8eqkf/BpIz/vaGI/6uSev+dhG7/qZOD/9LAvf/by8r/2srK/9fIyP/czc7/1MTF/4mAgP\
                8lIiL/RkFB/7Spqf/Tx8j/1MjI/8/ExP/Tx8b/0sbF/9HExP/RxML/0sTC/9HCvv/Nvrr/zb25/829t//SwLr/zLmv/519X/+feV\
                X/pHhK/5ZmNP+ZZzH/oGs0/6VtNf+hajD/qW4x/5RZG/+aXR3/unk5/8mGRv/LiEf/zIlI/8uJSP/Likz/yIpL/8aIR//Li0v/yI\
                tK/8WJTP/Gik7/w4hS/7J8Tf+OX0z/YkNWAEU3ewAxLowAMzGWADAvlAAxL5QAKyyUACgrlQApLJYAJyyYACYrmAApKpcAJyuaAC\
                ksmwApLJsA////AP///wD///8A////AP///wAoK5sAKCubACksmwApLJsAJyqZACcrmgAoK5oAKCuaACgrmgAoK5oAJiqZACYqmA\
                AqK5kAKiuYACcrmAApLJYAKS2VACoskgAmLJIAJi2RACovkAAsLo4AKi+MACwvigA4MWcAakk0AJ+Ggv/i0Nb/5NPZ/9/N0//hz9\
                T/3cvP/8y2s/+9pZn/pY5+/5Z/bv+NdmH/k3xn/5d/av+UfGf/mYJx/7Oek//PvLb/18fG/9rKyv/by8z/2MjJ/9XGx//Ft7j/j4\
                WF/zAsLf8nJSX/mpGR/9TIyP/Qw8P/0sbG/9DFxv/RxcX/0cTE/9LFxP/RxML/0cPB/9DCvv/Nvrn/zr24/8y8t//RwLn/zLqw/6\
                GAY/+ddlL/rIFT/72LVv/EjVb/u4JK/7iARP+0ej//mmEk/4xTFP+tbzH/1ZFQ/86LSv/HhEH/zIpJ/8yKSf/KiUn/yoxL/8yNSv\
                /Njkv/yotI/8aKSP/Gik3/wodP/6BtRP97UVD/XztlADwyfAAzL40ANDKWADAvlAAxL5QALCyVACgrlgApLJYAJyyYACcrmAAnK5\
                gAKCuaACksmwApLJsA////AP///wD///8A////AP///wApLJsAKSybACksmwApLJsAKCuaACgrmgAnKpkAJiqZACkqlwApKpcAKS\
                qXACgplwAqKpgAKiqYACcrmAAqLJcAKS2VACstkwArL5IAKzCRACovkAArLo0AKi+MAC8vhgA/NWgAa0o0AJ+Fgf/i0Nb/5tbe/9\
                3M0v/ezdP/4dDW/+DO0//ezdH/2cfK/9TCwv/XxML/1cPB/9XDwv/Xw8T/1cXF/9jHx//by8z/3c3N/9bGx//Etrf/rqKi/5eMjv\
                9iW1z/JyQk/ywpKf+Sior/0cXE/9PGx//QxMT/08fH/9HGxv/QxcX/0cXF/9HFxP/SxcL/0MPA/8/Avf/Nvrr/zr25/8y8tv/Rv7\
                j/zbqw/5d2Wv+Zc0//topb/8uYYv/MlFz/xo1U/8iOU/++g0j/lVwf/6NnKP+9fj//z4tK/8yJSP/Oikf/0IxL/8mHRv/IhkX/zI\
                tL/8yMSv/IiUf/yYpH/8yMTP/IjFP/tHtK/4RWR/9jQk8AUDRwADszgwAzMJIANjOXADUykwAyMJUALCyVACkslgApLJYAJiuYAC\
                csmAAqKpgAJyuaACksmwAnK5oA////AP///wD///8A////AP///wApLJsAKSybACgrmwApLJsAKCuaACoqmAAqK5gAKCqXACkqlw\
                ApKpcAKSqXACkqlwAnK5gAKiyXACkslgAqLZcAKS2VAC0tkgArL5IALDGSACwvjgAqL4sAKy6JACgthQA9NmwAako2AJl/ev/fzt\
                T/5tbe/9/P1v/fz9X/387U/93N0v/eztL/387T/+DQ1P/j0dT/4tHT/+HQ0v/h0NL/4NHS/9zLzv/ZyMr/28zN/8m7vP90bG3/Oj\
                U1/yQhIf8oJSX/VU9Q/5mOj//QxMX/1cfI/9LFxf/Txsf/0sbG/9LHx//RxcX/0sXF/9LFxP/RxML/0MG//86/vP/Nvrr/zb24/8\
                27tv/RwLn/y7it/49vUf+bdVD/uo9h/8GPXP+/i1P/xY5U/8CHTP+gaS//pGos/8eHR//TkVH/zYpJ/9WRUP/Yk1L/0IxL/9KQUP\
                /KiUn/zIxM/8iJSf/EhkX/yYpK/8+QVf+8g1P/lmRQ/2xIUv9bOm0AQjV9ADw0jAA0MpcANDKXADUykwAzMZYALCyVACotlwApLJ\
                YAKSyWACcsmAAoK5oAKCuaACgrmgAnK5oA////AP///wD///8A////AP///wApLJsAKSybACksmwAsLJoAKiqYACoqmAAqKpgAKi\
                uYACYrmAAmK5gAJyyYACkslgApLJYAKSyWACkslgArK5QAKiyTACkskQArLY8ALC+PACswjAAsL4oAKzCIAC8xhAA9Nm4AZ0g6AI\
                9yaf/Ww8n/5dXc/+LS2P/dztT/28zR/9vL0f/dzdL/3MzQ/9vLz//Yx8v/2cnM/9nKzf/ays3/2svM/9jIy//XyMr/2srM/8e6u/\
                97cnP/WlRU/3dub/+dkpP/wLS1/9PFxv/SxcX/08bH/9PHx//Tx8f/0sXF/9LFxv/SxsX/0sTD/9PGxP/RxMH/zsC9/8/Au//Nvb\
                n/zr24/868t//Sv7n/y7Wq/4RjRv+Yck7/wpNm/8WTX//FkVr/v4lS/6JsM/+HUxn/lFwh/61yNv+zdTn/s3U2/7t6Of+3djb/uH\
                c3/8SERP/HiUb/zY5L/8yNSv/Ojkv/zo9M/8iKS/+rdEP/glI7/2Q+aQBJN3wAPjWGADgzkgA6NZcAMTCVAC8ukwAyMJUALCyVAC\
                grlgAoK5UAKi2XACcsmAAnK5oAKCuaACgrmgAnK5oA////AP///wD///8A////AP///wAoK5oAKSybACsrmQArLJkAKiuZACormQ\
                AqK5gAJyuYACcsmAApLJcAKSyWACoslwApLJcAKSyWACsrlAAqLJIALS2RACwujwAtLo0AKy2KAC0wiwAuMIgAMTKHADE0hgA8Nn\
                IAYEZCAINlU//MuL7/5NTb/+TU2v/ezdP/3M3T/93O0//ez9T/3c7S/9zO0v/dztL/28zQ/9zN0P/bzM7/2MjL/9vLzf/bzc7/18\
                jK/9PGx//MvsD/xrm6/8+/wP/Uxcb/2MrL/9THx//WyMn/1MfI/9LGxf/Txsb/08bG/9LFxP/TxsX/08TE/9HEwf/Qwr//zsC8/8\
                +/u//Nvbj/zry4/868t//Twbr/yLKk/4VjRv+Yc0//vpBj/7+OWv+8hlH/pnA5/4xZI/+XYCf/lFwh/49XGv+TWR3/lFoc/41SEv\
                +SVhX/nWAi/6JmKP+qby//vH8//8yMTP/Vk1P/yIlJ/7J3P/+RXTz/akFJ/148cwBDNn8APDSMADkzkgA4M5UALy6TAC4tkwAyMJ\
                UALCyVACorkwAoK5YAKCuWACYrmAAnK5oAKCuaACcrmgAnKpoA////AP///wD///8A////AP///wAoK5sAKyyZACsrmQAsLJkALC\
                yZACormAAoK5UAKSyXACotlwAqLJcAKSyWACsslAArLJQAKSqTAC4tkgAuLpIALC6PACwujwArLo0AKi2MACsuiQAtMIYALi+EAD\
                E0hQA2NHoAW0ZNAH1bQv/DrrD/5NPa/+PT2f/g0df/3s7T/9vM0f/czdL/2szQ/9vM0P/bzdH/2svP/9zMz//bzND/2MrM/9nJy/\
                /bzM7/2srM/9fJyv/Zysv/2cvN/9fJyv/Xycn/1sjI/9THyP/Vx8f/1MbG/9PGxv/Uxsb/08XF/9PGxP/TxcT/08TC/9DBvv/PwL\
                3/zr+6/8+/u//Pvbn/zr24/828tf/Sv7X/v6eX/4tqR/+je1H/xpdo/7yJVP+jcDz/mWQw/7Z+Rv/eoWj/3p5g/9uYXP/XlVn/05\
                FT/9mWVv/NjEz/wYFE/7BzOP+aXyX/l10l/6tuM//Nj1T/voNY/5VlXf9sRWb/RjR8ADcuhAA7NI8AOTOOADMujQAyL5EAMjCRAC\
                4tkwArLJUALCyVACotlwAqLJcAKSyXACYrmAAnLJkAJyuaACgrmgAnK5oA////AP///wD///8A////AP///wAqKpgAKiuYACoqmA\
                ArLJkAKiqYAC4tlwAoK5UAJyqUACcqlQApLJcALCyVACsslAArLJQALi2TACgrkQApKo4AKSuNAC0ujQAsLosALS+MADIxhAA0M4\
                IANDN+ADY1gAA1NHoAV0ReAIRhRACtlpH/3s/V/+XV3P/g0df/3c/U/9zN0v/cztL/283R/9rM0P/bzND/2szQ/9rMz//Zy87/2s\
                vN/9vLzv/ay83/2srN/9nKy//XyMr/18jK/9fIyf/XyMj/2MjJ/9bIx//Vxsb/1MfH/9TGxf/UxsX/0sTC/9PFw//UxcP/08TC/8\
                /AvP/Ovrr/zr65/869uP/Pvbj/z723/9C9tv/OvLL/u6KQ/4xpRv+nfVT/2Kh4/8eSX/+RYC3/m2Yy/8iPWP/MkVj/zI1R/8+QU/\
                /Likz/1ZNU//m0dP/2sXH/35xd/82MUP/EhEn/oGUq/5JaHf+mbDH/l2A3/29EQf9fNmT/TzyFAD0ziAA8NZAAOTOOADQvjgAxL5\
                AAMzCRAC4tkgAuLZIAKyuUACwslQAqLJcAKSyWACcrmAAnLJkAJyuaACcrmgAoK5oA////AP///wD///8A////AP///wAqK5gAKi\
                qYACormQAqK5kAMC6XADAumAAsLpkALS+aACwumAArLJQAKyyUACsslAApK5EALS+VAC0tkQAvLo4ALi6NACwuigAtLogALzGJAD\
                MyhQAyMoQAMjODADEzgQAyM3wATEBmAI1sUgCTeGr/2MfM/+ja4P/g0tf/39DW/9zO0//azNH/287S/9vN0f/bztL/283R/9nMz/\
                /Zy87/2cvO/9nLzf/Yycv/2crM/9jJy//Xycr/2MnJ/9jJyv/XyMj/1sjI/9XIx//Vx8b/1MbF/9TGxf/UxsX/1cbD/9XGxP/Rw8\
                D/0MG9/8+/vP/Qv7r/zr64/827tv/QvLf/0L63/9C9tv/Ktq3/rpF9/5dxTv+edUz/q3xP/5NkNv+GViX/mmYz/7B5RP+pcDr/tX\
                k//7J2Ov+zdTr/qGsv/65wNP/BgUb/3Jld/+ShZv/momX/zo1R/6FnKv+PVx//ekgu/187R/9TNHIASzqGAEA2iwA9NpEANzKRAD\
                UwjwA0MZIALy6TAC8ukwArLJQALCyVACwslQApLJYAKy2YACgsmQAoLZoAKSybACgrmgAoK5oA////AP///wD///8A////AP///w\
                AqKpgAKiqYACoqmAAtLJYALy6YAC4tlwApLJYALC6ZACwslQAmKJAAKCqSACoskgApK5EALi6SACwtkQAoK4wALi+OAC4vjQAwMI\
                sAMzOMADAziQAwMYYAMTSGADEzgQAzNHoARD1nAJ+BcAB+Xkb/y7m9/+fZ3//f0tf/4dPY/9/R1v/cztP/287S/9vO0v/aztH/2s\
                3Q/9nLz//Yys7/2cvP/9nKzf/Yysz/2svM/9nJy//XyMr/2MjK/9fJyv/Xx8j/1sfG/9bGxf/UxcT/1MXE/9TFw//UxMP/1cXD/9\
                TFwv/Swr//z7+8/8++uv/Qv7r/z764/9G+t//Qvrb/zry0/9G+tf/MuK//mXti/5hwS/+ccUn/k2Y6/5JjNP+qd0b/vIRQ/72FTv\
                /HjFT/0ZNZ/86PVP/UlVj/xIRI/6NnLf+maDH/yIZP/+KdZf/enF//7alu/7x/Q/+ETxj/cEE2/3FFbwBOOH0ARDeGAEM3iQBBN5\
                AAOTOSADkzkgAxL5QALy6TAC8ulAAsLJUALCyVACwslQAqLJcAKi2XACgsmQAlK5sAKSybACcrmgApLJsA////AP///wD///8A//\
                //AP///wAqK5gAKiuYACoqmAAuLZcAMC6YAC8umAAoK5UAJymRACYokAAtLJEALS2RAC8vkwAsLZEALCyNACssiwAvLooALjCNAD\
                c2kQA0NY4AMTGHADQzhQAvMYEAMDOBADQ2fQA3N3YAQTtmALifmQB2UTH/tqGf/+DS2v/g09j/4NLX/+DT2P/h1Nn/3tHV/9rO0f\
                /Xy87/2szQ/9nMz//Zy8//2MrO/9nLzv/Zy87/2MrL/9jJzP/Yycv/18jJ/9fIyP/XyMj/2MjH/9jIx//XyMf/2MjH/9bHxP/Wxc\
                P/18bD/9TDwP/Qv7z/0L+6/9LBvf/Rv7r/z723/9LAuf/RvrX/z7ux/9O+tf/KsKH/hWFD/3ZRKv+hdkz/z51w/+qzgv/utYL/7b\
                F8//W4gf//wYb//7+E//+/gf//wYP//8CB//Ovc//Cgkn/oGUt/7J1Pv/Vk1f/9LJ1/7+BRf+DThf/f007/3FPZv9RNncASTmFAE\
                M3iQA/No4AOzWTADkzkQAxL5QALy6TAC8ukwAtLZYALS2WACwslQAqLZcAJyyYACgsmQAkKpoAJyuaACcrmgApLJsA////AP///w\
                D///8A////AP///wAqK5kAKiuYAC4tlwAtLJYAMC+ZACstmAArLJUALCyVADAvlAAtLY4ANDCJADQwhgA6MnoAQTd5AEs9egBLQH\
                0ARDt9AD03fgA/OH4AODN1ADY0ewAyMXkAMzR9ADY4fAA3OHYAPDxuAMu1twCFYkUAkHVk/9DBxf/j1tz/3dDV/9zQ1P/g1Nj/39\
                PX/9rO0v/ZzND/2MzP/9nM0P/Yy8//2MrO/9nLzv/Zy83/18jK/9fIyv/Yysv/18jJ/9jIyP/aysn/2cnJ/9vLyf/ezcv/3s3J/9\
                3Lx//aycX/2sjF/9fFwf/WxL//1cK9/9TBvP/TwLr/0b63/8+8tP/Pu7L/1sG4/8+5rv+Zdln/elQv/5twSP/Wp3r//9Gi///aqP\
                //0Zz//86Z///Pl///ypH//8yP///Ljf/7uHr/4Z9h/82NUP+zdTr/jFQa/5VbIf/ZmVn/87Fy/8CCRP+TWyD/nWY8/4tfYP9dO1\
                T/UDV1AEc6iABBOI0APzeSADgzlQAwL5QALy6TADAvlAAtLZYAKy6XAC0tlgAqLZcAKy2YACgsmQAlLJsAKCuaACksmwApLJsA//\
                //AP///wD///8A////AP///wApLJcALy6YAC8umAAtLJYAMC6XACsrlAAqK5MANTOXADYykAArKYMAMit3ADsxdwD///8AVDZg/1\
                Y5Xv9QNVoAQzBbAD0xYgBBOGoARj1vADo2dwAxMXgAMTN6ADY4fAA3OHYAOztwANfFygCfgW8AeVY5/7Oemf/e0db/39HX/9vO0/\
                /bztP/3dDV/9rO0v/bz9P/2M3Q/9jLz//azdD/2czP/9jLzv/Yys3/2MrM/9jJy//Yycr/18fI/9jIyP/WxsT/ybey/7unnP+vmI\
                n/sJiG/7ugjv+3nYz/tZyQ/8Kup//Tv7r/2MS+/9K/uf/Vwbv/0r63/866sv/OubD/z7qw/7WVgP9xSiT/iV81/96uhP//z5///8\
                qZ//S/i//3v4z//8WP///EjP//w4v//8KG//+/g//Tklf/k1cc/4VLD/+WWh//i1IW/5VbIf/HiUr/05RX/7R2N/+nai7/t3tH/6\
                pzVP9zSU7/WTJeAEQ4hQA/NosAPTaRAD43lQAyMJUAMC+UADAvlAAtLZYALC+XAC0tlgArLZgAKy2YACgsmQAlK5oAKSybACksmw\
                ApLJsA////AP///wD///8A////AP///wAqLJcALi2XAC8umAAvLpgAMzCWACwslQAuLZIAMC2PADAtigA8NIAAQzV1/0EzbP9GLV\
                3/UDZf/00xUv9FLVH/SjVh/0M5bP88NGsAPzhuADo1dAA3NXYANTV4ADs6dgA8Om0APz1nAOLS2ADIsrIAjGpPAI1xXf/PwMT/4t\
                bb/+DU2f/YzNH/2c3R/9rO0v/ZzdH/2MzP/9fKzv/Yy87/2cvO/9fKzf/Yycv/2crN/9fIyf/YyMn/2srK/9nIx/+0n5b/b1tM/1\
                I8LP9DLRv/RS4a/0kwHf9NMx7/Ri0Z/0IpGP+fiX7/zrqz/9rFvv/Tv7f/z7u0/9bCuf/TvbT/rZB//4lgPv+NYTf/pHVJ/+q5jP\
                //0qL//8qZ///JlP//y5X//8mT///EjP//xYz//8SJ///Fif/JiU//l1si/7NzN//BgUT/mF0h/51kKf+qbzT/pWov/5hdIf+vcT\
                T/xohP/7uBV/+IWlP/aUNj/0U1gAA6MocAOzSPADs1kwAwL5QAMjCVAC8ukwAsLJUALS2WACwslQAqLJcAKy2YACgsmQAjKpoAJy\
                uaACksmwAoK5sA////AP///wD///8A////AP///wApLJcAMC6UADAulQAyMJYAMzGWADMvjQBAN4cASTl4AEsuWwBQNkP/elRO/5\
                pvYf+pfmv/eVJB/1c2Kv9wUEX/e15c/3VcXv9aR00ASjg/AE89VQBPQVwARz9cAEhDYQBFQVwAOzZNAOPT2QDcy9AAvKSfAH5oWv\
                /Ju7//39LX/9rO0//YzdH/3dHV/97S1v/c0NT/39PX/9zO0v/Qw8b/0sTH/9vNz//fz9L/4dLU/9/P0f/ezc7/4M/P/8y3rP9VQD\
                H/a1I+/4xtVv+XeF7/h2ZM/19AJ/9dPCL/eFQ5/4RgRv9TNB3/pIp8/9W+tv/Wwbf/z7ux/9W+tv/XtaP/iF4//5NnP/+db0P/s4\
                NU//XDkf//0J///8mW///MmP//0pr//8WN//+/iP//w4r//8eM///Gif++f0b/jVQY/7t6Pv/HhUb/qGks/6NlJ/+eYCP/mVwf/7\
                x9QP/XlVb/zI1O/7R4QP+YYT3/dktJ/1c2aQBANH4AOzSPADc0lQAvLpMALy6TAC4tkgAuLZIALC6UAC0tlgArLZgAKCyZACYrmA\
                AkKpoAKCuaACksmwAqLJwA////AP///wD///8A////AP///wAqLZcAMS+VADIvlQAwLpUALi2SADQwjgBJPYYASjZvAEwtUf9tTl\
                b/nXVp/6V7aP+5jnv/cUs6/2VDNv+ObGT/fmBe/1Y+Pv9EMDX/Pi0z/zwqP/89LkT/OS5F/zYuRf83Mkf/QDxO/0I9Tv80Lj3/Pj\
                c+/0ZBQ/9RTVP/XFZc/2NfZf9bWFz/YF1h/2NiZP9mZGX/eHNz/3Fraf9YUk//Y1pX/25lYf9rYFr/b2Jd/3FjXP9rWlP/c15T/2\
                ROQP9WPiz/gmRN/6uIbP+tiWz/jGlM/2pHK/94UjT/mXBS/5hvUv9pRCf/ZkMo/8Cnmv/UvrP/2MC0/8eji/+edFX/d04q/51wRf\
                +sfVD/sYFS//TAkf//yZj/+sWU//nBjf/9wo7//8WO///Hjv/9vYX//7+D///Mjv/PkFP/ik8T/59iJv/HhEb/wX9B/7d3Of+XWx\
                3/sHAz/8qJSf/NjEz/y4pK/8qMT/+tc0X/e0w7/2Q7ZwBCM3oAPDSLADIwkQAzMJEALi2TAC0tkwAuLZMAMS+UACwslQApLJYAKS\
                yWACcsmQAmK5gAJyqZACosmwApLJsA////AP///wD///8A////AP///wApLJYAMS+VADIvlQAvLZMAMS6QAD02jABIPIEAUDNi/1\
                E2Qf+HYVv/tYp3/6h9af+ieGb/ZkMz/2pIPf99XFb/VTo3/zkjIv9GMjb/RzU6/zkqN/9LO0v/RztM/zgvQP85M0L/Vk5b/19ZZf\
                8/OkT/MS83/zk3Pf8uKjH/Hhof/zQzOP8jIiX/JCMm/zIwMf8qKCn/MCws/0M+PP8/Ojb/PTUx/zYtKf8xKCP/Mich/y0fF/82JR\
                v/PSod/z0nF/95XEf/nXtg/7ONcP+ZdFX/c08x/2lEJv+FXTz/mGxK/5FmRf+LYD//XjgZ/4dlS//IrZz/vpZ3/4xmRf+KYTz/j2\
                M7/5NmPP+LXzL/sIBR//C8jv//0KH//86e///Mmv//zZj//8eP///Jj///zpL//82S///NkP/xr3L/tXc8/6BjJ/+2dTf/xIJE/7\
                l4Ov+XWh3/woBC/9COTv/Likr/zItL/9KTVf+6f0z/gVAx/107VABMNngAPzaKADw1kAAyL5EALi2SAC4tkgAxL5QALy6TAC0tlg\
                ApLJcAKSyWACcsmAAlKpcAJCuaACksmwAoK5sA////AP///wD///8A////AP///wAsLJUAMjCWADAulAA3MpQAMzCRAD02jQA/Mn\
                EAVTVa/21LT/+ZcF7/sodw/6B1Xf+HX03/aEU3/3BPRf9nSkf/UDc1/1pERP9nU1X/RTU5/0k9Qf9nXGL/Zltl/0o/Sf9GPEb/ZF\
                1l/3Bpcf9RT1b/PDg//0xKUf9LR03/Pzk//1JRVP85ODv/QD9B/1RTVf9APj7/ODQz/2NeXP9pYV7/T0ZC/0k+Of9VSEL/U0U9/0\
                o6Lv9iTkH/YUs6/1E3I/+XdV3/pYBk/62EZv+HYUL/Z0Ik/3RLLP+Xa0j/jWA+/4hcOP+fcEv/b0Uj/142Ff+NZEL/l21J/45lP/\
                +gckv/tIRY/6R2Sf97UCT/mGs9/+y4iP/7xpX/8LmI/+uygP/7vor//8SM///Dif/4un///LyD///Bhv//wob/3Zpf/6FjKP+eYC\
                X/sXEz/6VlKP+sbC//xIJD/8qJSv/Mi0v/zItL/8mJTf+8gE//j1xC/2ZCTwBVOXcARDmKADw1kAA0MZIAMS+UAC8ulAAvLpMALy\
                6TACwslQApLJYAKSyWACYrmAAnK5gAJyqZACgrmgApLJsA////AP///wD///8A////AP///wAtLZYAMjCWADIwlgA2MZMANzKPAE\
                E4iwA8K2T/UjdG/4VeUP+jeF//rYFp/6N4YP9vSzj/a0o7/3FTS/9YPz3/Uz09/2ZSUv9iUFL/OSst/1lLT/9zZ2v/YVhd/0E7P/\
                9LRUr/ZV5l/2ReZP9OSE7/R0FH/05ITv9QSlD/S0lP/1lYW/9CP0P/UE5P/15cXf9FQkH/R0JA/3Ntaf9tZGD/SUA8/1FHQf9kVk\
                7/XExF/1NCNv9uV0f/aVA+/2VIMv+bd13/pn9i/6Z+Xf+GXj7/aUIj/3xSMP+abEr/lGRB/5FiPf+ZaUP/ek8q/2A4Ff96Tir/nX\
                BL/7WGXv+2hlz/wpFl/8eWZ/+Yaz3/iV0w/72MXf+3hlX/n29A/5ZkM/+4gEz/6613/+6wev+zekX/pWs2/9iYYf/ysHX/x4dN/4\
                xRGP+PUxj/rmwy/7RyNf/Kh0r/yodK/8uIS//OjU3/yYhJ/8aGSv/BhVL/nmhK/3ZNWABZOW8AQTaEADkyjQAyL5EAMjCVADAvlA\
                AwL5QAKyuUACsrlAAqK5MAKi2XACcrmAAoLZoAKSybACksmwApLJsA////AP///wD///8A////AP///wAtLZYAMzCWADYxkwA4Mp\
                AANjGLAEo+iABELWH/VjdB/5BnVP+qfmL/qX5k/6N6Y/9hPiz/d1VG/3ZYUf9TOjn/VUFC/2VQUf9UQ0T/PzEz/2JVWP9tYmX/SU\
                BD/zUvMv9WUVT/Z2Fk/1NNU/86Njv/SUVL/0M/RP9DP0X/TEtO/0xJTf85ODv/SklL/1BOT/86NjX/UEtJ/2xmY/9TSkb/PTIt/1\
                ZLRP9XSUH/STkv/1I/Mf9YQjH/VTon/3lXPv+hel3/rIRl/5hvTv95UDD/Z0Af/4JWNf+VZ0P/lGVB/5ZkQP+VYz3/i1w1/29DHv\
                +AUiz/qnpR/8WTaf/Bj2X/wI1i/8qZbP+tflD/hFks/4ldMv+RZDb/ek0g/3RHGP+aZjX/uH9L/7Z8R/+bYjD/ilQd/6VrNP+oaz\
                P/nmMp/6lqMf+0dDj/vXs//9CKTv/Oikv/zYpN/8+LTP/Ni0z/yYlJ/8yLTf/Eh1L/mGI8/25ESABeNl8ARTeAAD01jQAyL5EALS\
                2TADIwlQA0MpYAKiuUACorlAAqK5QAKCuVACcsmQAnLJkAKSybACksmwApLJsA////AP///wD///8A////AP///wAsLJUANjGTAD\
                kzkQA6M44AOzSLAP///wBKL1//XT1F/5dtVv+xhGj/o3pi/5tzXv9YOCX/d1VF/2hNRP9JMzD/WkZH/2xXV/9LOjz/QTIz/2daXP\
                9kWlz/QTo8/zgyNP9dWFv/ZWFl/0tFS/84NDn/UExR/0JBRv8/PkH/V1RY/0RBRf8+PT//Tk1P/0lHSP89ODj/VlFP/2hgXf9MRE\
                D/PzUv/2FTS/9VRTz/Rzct/11HOP9dRTP/Vzom/4ljSf+helv/sIVl/49kRf9uRif/dU0r/5BiP/+ZaEX/lWI+/5VjPf+VYz3/lG\
                M7/3lMJf92SST/pHRM/8+bcf+8il7/uIZb/8STaf+ld07/eVEq/5FnQP+1hlz/kmU6/4VWKf+ueEj/qXE//5pjMP+yeEL/vH9F/6\
                NpMP+QVx//qW0y/9OSVf/cl1n/zotO/8yJTP/KiEv/zIlM/86KS//Likr/y4pK/9KRVP++f0z/kFo0/3NGO/9YN03/Tjp+AEQ6jg\
                A3MpEAMy+SAC8ukwA5NZYALCyVACwslQArK5QAKCuWACgrlgAnK5gAJCqaACgrmgAnKpkA////AP///wD///8A////AP///wAvLp\
                MAMzCSADcxkAA2MYsA////AP///wBML1v/Z0RK/6F2Xv+3im7/oHdf/45pVv9gPyz/fV1M/2lORf9KNDH/V0JC/2BOTv9DMzP/Tk\
                FB/1tQUf9gV1f/RDw+/0E7Pf9ZVVf/WVVZ/0I+Qv87Nzz/UE9S/0JBRP87Oj3/U1BU/z48Pf9BQEL/TkxM/0A+P/9IQ0P/Uk1L/2\
                JaV/9USUb/PTMs/15QSP9TQjj/Szgu/1Q+Lv9hRjP/Y0Mt/5NtUf+jeVr/t4lo/4xhQP9sQyL/fVEu/5JiP/+SYj7/k2E8/5ZjPf\
                +VYjv/lWM7/39RKv9qPhj/mGk//9mkd//AjmL/uIhc/8WVbP+TaEP/fVUz/7CEYf/TpH7/nnBJ/3lOJv+2f1D/0Zdk/8iNVf/Lj1\
                X/yIpP/8mLUP/YmFz/15VZ/8KARv/Fg0j/0I1P/8yJTP/MiUz/zIlM/8mHSv/Jhkn/zotO/9GPU/+2eUf/lF46/5FeTf9nQk7/UT\
                d0AEE2hwA3MY8ANjGTAC0skQAxL5AAKyuUACwslQAqK5QAKSqTACgrlQAnLJgAJyuYACcqmQAnK5oA////AP///wD///8A////AP\
                ///wAuLZIANzKRADcxkAA7M4sARjmAAE0yYv9PNUb/dlFU/6J3Yf+yhmz/m3Nd/31aRf9nRjX/cVRI/15GQP9JNjL/V0RB/1NBPv\
                9GNjP/V0lG/1RISP9PRkf/Rj8//0Y/Qf9RTU//Uk5Q/0JBQ/85Njr/SEdK/z06Pv9DQET/S0pN/zk3OP9FREb/RUNE/zs4N/9JRE\
                L/V1FO/01FQf9LQDv/SDs1/1REPf9RPzb/STUq/1M9K/9WOyb/cE81/5xzVf+pfFv/uIpn/4tePP9kOxz/hFYz/6BvSv+UYjz/lG\
                E6/5dkPf+QXjf/nWpC/4ZVL/9jORP/mGlB/9Gdc/+/jGP/vo1h/8uab/+YbUj/bUgm/7OHZP/SpH3/mWxE/3lNIP+3hFD/1Jxm/8\
                eLVv/KjVj/wYRM/8yOU//RkFb/y4tP/8uITf/KiE3/yohN/8qITf/LiEv/zIlM/8uIS//Pi07/1ZFW/8aGTP+lajX/j1Yn/6NsTf\
                +HWVT/Yj1c/0IyeABAOI8AODOVADIukQApKpMALi2SAC4tkgAuLZIAKyuUACoslwAnLJkAKSqYACYqmQAnKpkA////AP///wD///\
                8A////AP///wAvLpMANzKRADozjgA8NIsARjqBAFM0X/9bPkr/gFpZ/6B1Xv+tgWf/mXBY/31ZRf9qSjn/blFF/1xFPf9MOTP/WU\
                ZB/049OP9CMi3/WElF/1JGRP9MQkL/QTo6/0Q/P/9RTU7/T01N/0JBQ/8+PD3/QkBB/zk4Ov9DQkT/TEpL/zY0Nf9FQ0T/RUNE/z\
                UyMf9IQ0H/WVNP/0pBPf9EOjT/Sj03/1NDOv9KOC3/SDQo/1g/LP9WOSP/b0wx/6uAYf+rfl3/soJg/31SMP9mPBv/iVo2/6FtR/\
                +TYDn/lmE4/5diOv+TXjb/om5E/49dNP9oPRf/i1w0/72LYP+4hlv/xJFl/8mYbv+RZT7/b0kl/6uAXf/PoHr/nXBH/3pOIv+ve0\
                j/zJJd/8OIUv/GiVT/xolQ/8qKUP/KilD/yIhO/8mGTP/Nik//zotQ/82ITv/KiE3/zYpP/9OPVP/Wkln/yohP/65vOv+YXiz/lV\
                wu/6NsTv+TZWH/bEZm/0MzeQA/N44AOjWXADEvlQAsLJUAMS+UADAvlAAsLJUALCyVACkslgAmK5gAKSqXACQolwAoK5oA////AP\
                ///wD///8A////AP///wAzMJIANzKRADozjgA6MooASDp+AFExWf9hQk3/jGRe/6d7Yf+ugmb/m3Na/3tYQv9tTTz/aExA/1hBOf\
                9RPjj/VkU+/0g3MP8/MCn/VUdB/1RKRv9GPjv/QDk3/0ZBP/9NSkn/R0VF/zw6O/89PD3/PDw+/zY3OP9DREX/R0hJ/zAxMv9AQE\
                D/REJB/y8sK/9IQ0H/WFJP/0U9Of88Mi3/Sz42/009Nf9CMSb/SjYq/1g/K/9VOCD/c08z/7SGZf+tfVz/qHlW/3lMKv9qPhz/kF\
                45/59rQ/+UXzf/lmE3/5diN/+QXDL/omtA/41bMf9wQhr/iVow/7iGWf/AjWD/xpNl/8qZav+abUT/fVUv/7GFX//Qn3j/n29H/4\
                FSJ/+1gE//zZNe/8OGUf/FiFP/yYtS/8eHUP/IiE7/yohP/8uITf/SjFL/1pBX/9OOVf/SjVX/y4hP/8WDS/+5eED/pWcx/5ZaKP\
                +YXjD/pmtA/5VgRP+RYWL/b0lp/0kzeAA6M4oAODOVADQwkwAxLpQALy6UACwslQAsLJUAKyyUACkslgAlKpcAKSqXACUpmAAoK5\
                oA////AP///wD///8A////AP///wAxL5QAODKQADgyjgA8NIwA////AE0tU/9gQEn/kWhf/6uAZv+xhGn/mnJa/3RRO/9wUUH/Y0\
                k8/046Mf9MOzX/UkA6/0U0Lv9AMiv/U0ZA/1JHQv9AOTb/PDc1/0dCQP9LSUj/PTs8/zUzNP87Ozv/PDw8/zo6PP8/QEH/QUFD/z\
                IyMv9AQED/QT49/zAtLP9HQkD/V09M/0M6Nf88MSv/TT84/0k6Mf9BLyX/SzYp/1Q6Jv9ZOiP/f1g6/7KEY/+rfFr/onNQ/31PLf\
                9zRSP/kV85/5lkPf+VYDb/mWI4/5dfNP+RXDH/nmg7/4xYL/9wQhj/hFUs/7iEWP+/jF//vIla/8WUZf+bbkT/elEs/7CCXf/Kmn\
                X/l2hD/31RJ/+3glH/zZRf/8GGUf/HiVL/y41W/8yMVP/Qj1f/1pJZ/86LUv/IhEz/yYRM/798RP++e0T/sXI8/6VnMv+YXCn/kF\
                Uk/51gMf+pbUD/qm9I/3tJMP9zRkn/XjpX/0w2eQA8NIsANTGUADUwkgAzMJYALi6WACwtlQAsLZUALCyVACkslgAqLZcAKCmXAC\
                YqmAAnK5oA////AP///wD///8A////AP///wAuLZIAODKQADgyjgA6MooA////AE0sTv9fP0j/kmth/62BZ/+ug2f/kmtT/2lINP\
                90VEb/YUc8/0o3Lv9JODL/Tjw1/0U0Lf9CMyz/TkE7/0tBO/88NDD/OjQx/0ZDQf9JRkX/Ojg4/zQ0NP89PT3/PDw8/zs7O/88PD\
                z/PDw8/zg4OP8+Pj7/PDo5/zg1Mv9FQDz/UEhF/0M6Nf8/NS7/Sz42/0g4Lv9FMyb/SzUp/1E3Iv9bPCP/h19B/6x+XP+tfVn/m2\
                tH/39SLv93SCP/kmA4/5hjOv+XYDf/m2M4/5piN/+YYTb/nmk+/45cMf93Rx7/f08m/7F9Uv/IlGf/v4xf/8qZav+dcEf/akIc/6\
                +BXf/SoXr/nW5I/3pMJf+3glP/0Zhk/8SJVf/Gi1X/y41W/8eHUf/NjFT/0I1V/8SCSf+0dDz/rGs2/55fK/+aWyj/mV0q/51hMP\
                +hZDP/pGc3/65yRf+scUX/m2I7/3pILP9eMiz/TS1B/1c4eABDOY0AOTORADgzlQA5NZoALC2VACwslQAsLJUALCyVACotlwApLJ\
                YAJiuYACYqmQAnK5oA////AP///wD///8A////AP///wAvLpMAODKRADcxjQA7M4sA////AE0tTP9jREz/lGxh/6uAZv+rgGT/km\
                tU/2ZFMf94Wkr/Ykk+/0o2Lv9HNi7/SDYv/0M0LP9DNi//Rzw1/0c+Of87My//OjUy/0VCQP9EQUD/NjY2/zU1Nf86Ojr/OTk5/z\
                k5Of84ODj/ODg4/zs7O/88PDz/Ojc2/zw5Nv9CPDn/Rz87/0I5NP9BNi//SDoz/0U1K/9FMyf/SDMl/1A0IP9fPyb/jmVH/6x+XP\
                +xgV3/lGRB/3lKJ/93SCT/lF85/5lkO/+WXzX/m2M6/5dgNP+YYzj/nWc8/5NhOP9/Tib/f04m/616UP/LmGz/yJRp/82cb/+idE\
                v/dk0o/7mLZv/YpX7/n29J/3hLJP+xfVD/1Jxp/8SLWf+6gE3/uH1I/65yP/+nazb/pWc0/6BjLv+gYy7/pGQy/59hLv+jZDP/p2\
                k3/7BxQf+ydEX/sHJF/6xwQ/+gZj3/l143/41YPP9rPDH/UzA8/104cQBHOokANzGPADcylQA7NpsANjGTACwslQAsLJUALCyVAC\
                kslwAqLJcAKiuYACormAAnK5oA////AP///wD///8A////AP///wAuLZIAODKQADgyjQA9NIgA////AEwsS/9jREv/k2tc/6yAZ/\
                +rgWb/j2pT/2lHNf94Wkz/YEY8/0c0K/9HNS7/RTQt/z4vJ/9CNS7/Qjgx/0Q7Nf87MzD/OjUz/z88Ov9APTz/NjY2/zQ0NP82Nj\
                b/NjY2/zY2Nv82Njb/NjY2/zg4OP85OTn/ODY1/zo3NP8/OTb/Rj05/0A2Mf88Miv/Rjgv/0IzKf9CMCT/RjEh/08zH/9kRCv/jm\
                ZH/6x+XP+wgF3/kmRA/3RHJP94SSX/k184/5plPP+SXDP/j1kw/4lUK/+IVS3/iFUt/4VVLv93SCT/d0om/5FjPv+peVL/oXJL/6\
                d4Uf+JXjr/f1Yy/7KCXv/BkGz/k2NA/3BEH/+QXzT/qnVH/6x0Rf+faDj/o2o6/5tjMv+XXSv/lVsp/5ldKv+jZjL/rW46/7NyQP\
                +2dkT/s3RD/7ByQ/+pbED/omg7/5lfNf+XXjT/m2E5/5hhP/+ATzz/YzxG/1ozYgBHNoAANzGNADEtkAAyLpEANzKVACwslQAsLJ\
                UALCyVACwslQAqLZcAJyyZACoqmAAnK5oA////AP///wD///8A////AP///wAuLZMANjGQADgyjQA9NIgA////AE4tTP9hQUj/j2\
                da/6yAZ/+tg2n/j2pT/2ZFNP92WUv/XUQ5/0UyKv9GNC3/QjEp/z4tJf9BMiv/QTYv/0M5Nf87MzH/NjEw/zo3Nv87ODf/NTU1/z\
                MzM/8yMjL/MzMz/zMzM/82Njb/NDQ0/zU1Nf80NDT/NjMy/zYzMf87NjP/RT04/z0zLv83LSb/RDcu/0ExJv8+LB//Qi0e/0wwHP\
                9rSzH/j2dI/6d6WP+sfFj/mGpF/3ZJJv98TSj/jlw3/5tmP/+PWzP/hVAq/3VFHv9yQh3/aj0X/2tAHf9sQSD/bkQk/21EI/9qQi\
                H/aD8f/3ZLKv9lPR3/dEor/6N0Uf+ldlP/iVo4/3BEH/9sQBf/dUYa/4pWK/+TXDH/l18y/6JpOv+tcD//snVC/7V2RP+wckD/rW\
                48/6ttO/+kZzf/pGc5/55iNv+ZXTL/m2E2/5ZdM/+XXjP/ll82/5BaN/+TXkT/b0ZM/1YvWwBMNnsAQzmQADQvjgArKYwANzKUAD\
                IwlQAsLJUALCyVACwslQAqLJcAKi2XACormAAoK5oA////AP///wD///8A////AP///wA1MJIANjGQAD01jQBBOIgA////AE0tU/\
                9hQkr/kmtj/6p/af+rgWf/kGpS/2hHNP95W0v/Uzow/z0rJP9CMSv/QjEr/z8wKf8+MSr/PTIs/z40Mf86MjD/NC8t/zUzMv83ND\
                T/NTMz/zIyMv8xMTH/MjIy/zU1Nf80NDT/MjIy/zMzM/82NDX/NTIy/zUyMP86NTL/PjYy/z0yLf85Lyj/PzEp/0IyKP9ALiD/PC\
                cY/0gtFv9rSjD/lWxP/6x/Xv+tf13/lWdF/3tOLP97TSr/kmA6/51pQ/+NWTP/eUgl/3tKJv+BUTD/h1k4/35TNf+AVTj/f1Q6/4\
                BXPP99VTn/flU4/4VbPP9xSSr/e1Iu/6V4VP+mdlH/kmVB/4FTL/96TSb/eUoi/5FcMv+ncEP/p29B/6duQP+obj7/qG0+/6ZpOf\
                +jZjX/oWQy/55iM/+bXzL/ml4x/5pfM/+aXzX/mWA1/5hfN/+YXzn/mWA6/5ZgQP+MWD//b0RE/1MzSABWNG0ARzuIADo0kgA2MZ\
                MAODOVADIwlQAsLJUALCyVACwslQArLpgAKSyXACgsmQArK5kA////AP///wD///8A////AP///wA1MJIANjGQAD01jABCOYkA//\
                //AEwsUv9fQUn/kGlf/6p/aP+rgWb/kmxT/2hHNf97XU3/Ujov/zgmH/89LSf/QDAq/z4vJ/8+MSr/PDIr/zsxLv85MS//NTEv/z\
                UzMv81MzL/MjAx/zAwMP8vLy//MDAw/zExMf8zMzP/MjIy/zExMf8yMDH/Mi8u/zMwLf84Mi//OTEt/zkvKv86Lij/Pi8n/z8wJv\
                8+Kh//OyYX/0UqFP9nRy3/j2dK/6l8W/+tfVv/k2ZE/3dKKf97TCn/j146/5pnQf+OWjb/f00p/3NFI/9zRSX/fE8v/4BUNf9/VD\
                r/bUYt/2pEK/9lQSf/ZUAm/3BLL/9uRyv/e1M2/6t+Xf+uf13/k2ZF/3VKKP9yRiP/f1Ep/5ZjOv+kbkP/n2c7/55mOP+bYTX/l1\
                4w/5VaLf+WWyz/lVor/5hcLf+bXzL/m180/5tfNv+ZXjT/mF83/5hfNv+WXjf/l184/5RfPP+NWUD/cEVD/1AwQ/9UM24ARTiHAD\
                cxkAA3MpUAODOVADcylAAtLZYALCyVACwslQApLJcAKSyXACgsmQArK5kA////AP///wD///8A////AP///wA1MJIANTCPAD01jA\
                BEOYYA////AE4uVP9iREz/kWpg/6l/av+sgmj/k21W/2hGNP96XEz/WD80/zspIv85KSL/Pi0n/z0uKP88Lyj/Ny0n/zctKv83MC\
                3/NTAv/zQyMf8zMTD/MS8v/zAwMP8uLi7/Ly8v/y8vL/8wMDD/MjIy/y8vL/8sKiv/Ly0s/zAtK/80Liv/NC0p/zguKf87Lyn/Oy\
                0m/z4vJf8+Kx7/OCMV/0YrFP9pSS//jGZI/6Z5W/+sfl7/lGZE/3ZKKP9+UC7/lGI+/55qRP+TYTv/h1Yx/3pLJv9vQR//ckYl/2\
                xDI/9wSCn/b0co/4VcO/+XbUn/jGNA/4hgPP99VDP/c0sr/45jQP+VZ0X/g1Yz/3BEIf92SST/gVEq/41ZMf+OWjD/l2A0/5ZfNP\
                +WXTH/mF4y/5xgM/+dYTP/nGAz/5tfMv+bYDT/ml4z/5peNf+bYDb/mF83/5deOP+XXzj/ll45/5ReO/+PW0H/bkE9/08uO/9YNW\
                8ARDiKADYwkAA0MZcANjGTADUxlAAsLJUALCyVACwtlQAoK5YAKi2XACoqmAArK5kA////AP///wD///8A////AP///wA1MJIANz\
                GPADw0jABEOYYA////AFIwVP9kREz/kGlh/6l+av+rgmn/kWtT/2ZFM/90Vkf/YUg9/0czK/85KCH/Oioi/z0uKP86LSb/NSkj/z\
                MqJv81Liv/NC8t/zEuLP8vLSz/MC4u/zAwMP8tLS3/Li4u/y4uLv8uLi7/MTEx/y4uLv8tKyz/Lyws/zAtK/8wKyf/Miom/zctKP\
                86Lij/OSsk/z0tJP8+KyD/NSEU/0IoE/9oSC//jWdK/6p/X/+tgF//k2ZG/3RJKf9+UC7/jl86/5lmQv+SYDv/lGI8/5plQP+aZU\
                D/nWpE/41eOf+BUy3/l2hB/82bcP/xvZD/3qt+/8mYbf+vgFf/jmA5/3lMKP9+US3/f08s/4lYMv+VYTr/mmQ8/5xlPf+cZDv/l2\
                A3/5lgN/+ZYDX/nGI3/51hNv+cYDX/ml4z/5pcMv+bXjP/ml41/5tgNv+bYDj/ml85/5lgOf+aYTr/mF86/5dgPv+TXUD/cEE3/1\
                IuOf9bNmYASzyKADkykQA0MZcANzKUADUxlAA2MZMALCyVACwslQApLJYAKSyXACgsmQAoLJkA////AP///wD///8A////AP///w\
                AuLZIAODKOAD41iQBBN4QA////AFEvUv9jREz/kGlg/6h+af+qgGb/jmlQ/2REMP9zVkb/Ykk+/0YzK/8zIxz/OCgg/zssJP83KC\
                L/MCUf/zIoJf8zKyn/MSwq/yonJf8rKCf/MC4u/y0tLf8pKSn/LS0t/y4uLv8rKyv/LCws/ysrK/8tKyv/Ly0s/y8sKv8sJyX/Ly\
                cj/zQqJf85LSf/MyUf/z0sI/9ALCH/MR0P/z0jDv9lRSz/kGlN/7GFZf+ugGD/k2hG/3JIJ/93Syn/lmZD/5tqRf+PXTj/kV86/5\
                ZiPf+VYTr/mmdB/5BeOf95TCb/eU4p/5tsRv+sfVT/oHJJ/5tuRf+gcEj/k2VA/41eO/+MXTr/ilk2/5JgPP+WYTz/kl44/5VeN/\
                +ZYjr/lmA4/5hfOP+YXzb/m2A2/5pfNf+ZXjL/mV0y/5tdM/+dXzb/m182/5tgOP+bXzf/m2A6/5leOP+YXzr/mF86/5lgP/+YYk\
                P/e0o6/1szOP9YNFH/Ujl9AEA2jwA+NpUANzKUADcylQA2MZMALy6TACwslQAtLZYAKy2YACktmgAoLJkA////AP///wD///8A//\
                //AP///wA0MZIANTGPADkziQD///8A////AE4vUP9kRU3/k2xi/6iAaP+pgGX/kGpS/2hINP92WEb/Ykg8/z8sIv8uHxj/OCcg/z\
                orI/8zJR//LyMe/zAnI/8zLCn/Mi0r/yUjIv8mIyL/MC4v/ysrK/8mJib/Kysr/y0tLf8pKSn/KSkp/yoqKv8rKSn/LSsq/y0qKP\
                8pJCL/KiMh/zEnIv86Lij/LiEa/zsrIv8+KyD/LhoL/z0lEf9jRSz/i2VJ/6uAYP+oe1r/lmlI/3dNLP94Syr/j188/5VlQP+SYT\
                3/mWZA/5RiPP+NWzb/mWhB/5hnQv90Sij/Zz4e/39WNP+QZUL/jWI//4lfPP+QZUL/jmE//45hQf+SY0H/kmNA/5RkP/+VYjz/k2\
                E5/5VgOP+XYTn/l2A6/5deN/+YXzj/mmE4/5pfN/+ZXjT/m2A2/51fNv+dXzf/nGE5/5tgOP+aXzf/m2A6/5pfOf+YXzr/mGA8/5\
                ZePf+ZY0L/jVk+/29ANf9WMTz/VzFlAEM3iQA/NpIANzKUADQxkwA1MZQANjGTACwslQAsLZUAKSyWACotlwAmK5gA////AP///w\
                D///8A////AP///wA0MZIANTGPADozigD///8AUztzAEwuTv9hQkr/k2xi/6qBbP+sgmf/k21V/3BQO/9wUkH/ZEw//0QwJv8sGx\
                X/NCQd/zkpIf8xIx3/LiId/ysiH/8wKSf/Mi4s/yQgH/8gHh3/Liwt/ywqKv8jIyP/Jyco/y4uMP8lJif/JiYo/ywsLP8oJib/KC\
                Yn/y0rKv8nIiH/JR4b/y4kIf87Lyv/LB8Y/zkpIf85Jx3/LhoL/z8nEv9cPyf/g15D/6l+Xv+nelr/n3BP/4BUM/93Syn/iVo3/5\
                ZmQv+UYj7/l2VB/5FfO/+OXTf/nGtG/5BiPf9ySCX/bkQm/4peP/+OY0T/j2VF/5BlRv+PZEP/j2JC/5BjQf+VZUT/lWVC/5ZmQ/\
                +WYz3/kmA4/5NfOP+SXjj/l2E7/5lgO/+ZYDn/m2E7/5tfOP+aXjf/mV40/5tfNv+aXzf/m184/5tgOP+bYDj/m2A6/5tfOf+ZYD\
                v/mWA9/5dfPv+WXj7/lmA//4RROP9fNTP/UC1JAE04fwBBN48ANjGQADMwkgA2MZMANTGUADEvlQAsLJUAKCuWACotlwAqLJcA//\
                //AP///wD///8A////AP///wAxL5AAODONADw0hwBEOH8AVTtxAEorS/9gQEj/kWxh/6mBa/+sgmj/lW9W/3ZVQP9lSDb/a1BE/0\
                85L/8qGRL/KxwV/zkpIv8wIhv/KR0Y/yUcGf8sJSP/MCko/x8bG/8dGxv/Kigp/ygnKf8iISL/JyUm/ywsLv8iIib/JyYo/y4sLf\
                8iISP/JSMk/zAsLf8mIiL/IRsa/ycfHf87Lyv/Kx0Z/zMkHP81Ihn/LxsP/zAaBf9SNSD/f1xA/62CYv+xg2L/pnlX/4FVNP9pQB\
                7/hlo3/5prR/+OXzz/i1w4/4xbN/+WYz//pHJN/4ZYM/9qQB//c0kp/5NoRv+LYEH/jmRE/5RoSf+VZ0f/lGZE/5NlQ/+UZEH/k2\
                NA/5VjQf+WZED/k188/5ZiP/+XYTz/l2E7/5lgO/+ZYTz/mWA5/5pfN/+aXzf/ml83/5tgOP+bXzj/ml83/5pfOf+aXzn/m2A6/5\
                pfOf+bYDv/mGA8/5hgPv+UXDv/l2FA/49aO/9oOyz/UjA9/1s7egBFOIoANC+OADMvkgA2MZMANzKVADYxkwArK5QALCyVAC4ulg\
                ApLJcA////AP///wD///8A////AP///wA0MY0ANjKMADs0hwBCOYUATz59AE4yXv9XPEX/hWBS/6R7Y/+qgmf/nHZc/31cRf9kSD\
                f/aE5B/1I8NP8rGxb/KxwW/zYmIP80JiH/JRoV/yIZFv8qIR//LCUk/yIfIP8fHR3/IB8h/yMiJf8mJSj/JiMn/ykmKv8gHyL/Ji\
                Uo/y0sL/8jIiX/HRwe/zQwMf8nIiL/GBEP/yYeHP8vJCH/LyIe/zcnIf8xHxn/LRoT/zIdCv9FKhX/elY9/6h+YP+rfl3/p3hW/3\
                VLLP9sQiL/j2JE/5BjRP9zSS7/gFY7/4FWOv+GWjz/lWdH/4JWNv9jOxv/ckgp/5BlRf+HXkD/jmNG/5BlR/+PY0b/jWFE/5FkQ/\
                +PYkH/kWJC/5JjQf+SYUD/lGJA/5djPv+WYTz/mGE9/5hhO/+ZYDv/mWA7/5pfOf+bYDr/ml85/5tfOP+bXzj/m2A6/5tgOv+bYD\
                r/ml85/5tgOv+aXzv/mWA7/5lgPf+XXzz/mGI9/5FcPv9/TTb/YTk+/1UwYgBCNogAQDePADcykQA2MZMANjGTAC8ukwAuLZIALC\
                yVACwslQAqLZcA////AP///wD///8A////AP///wA1MY0ANTGLADcyiABAOIcASjx5AEMrWP9WPUb/iGRb/511Xv+lfWL/onti/4\
                JgSf9iRTX/ZUs//1M9Nf8uHRj/KBcU/zMkH/81KCT/IxcT/x0TEP8uJiX/LCYm/x8cHf8aFxn/IR0h/ycmKf8kIyf/IiEl/ycmK/\
                8dHB//HRwh/ysqL/8oIij/IBwg/y4rLP8lICH/FgsM/yYeHv8rISD/KR0b/zAhHP8vHhn/KhcP/ygSAP8+IhD/elQ9/6p9YP+rfF\
                z/s4Nh/3xQL/9qPyD/f1Q0/4xgQf+KXkH/tIVo/7GCZf+GWj3/fVI2/4FWOv9jPB7/Zj8g/5ltTv+RZ0n/jmRE/45jRP+LX0D/kG\
                NF/5JlRf+PYkL/kWJB/5NjQv+UY0D/k2E//5diP/+ZYj7/mGI9/5liPv+aYTz/mGA7/5lgOv+bYDr/ml85/5pfOf+aXzn/ml85/5\
                pfOf+aXzn/m2A6/5tgPP+bYDz/ml87/5lgPf+YXzz/mWI+/5pkQ/+LWD7/Zzw4/1cvVQBHN4IARDiKADYxkAA1MZQAODOVADYxkw\
                A0MJMAMi+VACwslQApLJYA////AP///wD///8A////AP///wA0MY4AMzCNADcyiABDOYUAQjZ0AEwzY/9UO0f/gF1X/5x2Yf+qg2\
                n/nHhg/4RiTP9mSTj/bVNH/19JQv8vHhr/IA8I/y8gHf85KSb/IBQS/xkNDf8qIiH/LSUl/yMeH/8ZFRf/Gxgb/ycjKP8nJSr/Hh\
                of/ykmKv8oJCr/Hhof/yonK/8lIib/Ih8j/ywoK/8nIiT/GA8R/yAXGP8uIyH/LiAe/y0dGf83JB//MBsV/ycQAP86HQz/fVdA/6\
                2AZf+rfFz/wI9t/4RWNf9kOhn/fVIz/49iQ/+gclT/ypl8/8mYe/+vg2f/o3hc/4NaQv9lPSL/cEgs/5tvUf+QZkj/i2FC/49kQ/\
                +RZET/kmVE/5JlRf+QY0H/kGNB/5VlRP+VZUL/lmRC/5diP/+WYj7/lmA8/5dhPf+aYTz/mWA7/5hgO/+bYDr/ml85/5pfOf+aXz\
                n/m2A6/5tgOv+aXzn/ml87/5xhPP+cYTz/ml87/5lgO/+WXjv/lV87/5ljQv+XYUb/d0c8/1MyQv9VN3UASzyJADozjgA2MZMAOj\
                WXADgzlQA1MZQAMS+VAC0tlgApLJcA////AP///wD///8A////AP///wAzMI0AODOMADw1iABCOoUAUUB0/1M7Yf9GLzz/aktJ/5\
                55Zv+wiXH/nnpi/4VjTf9iRTX/dltO/2xVTv80IR7/HQkE/y0dGv83KCb/IRUT/x0REf8cExP/KSEj/y4oKv8cGRv/FxAX/yQeJP\
                8rKS7/HBoh/yMiJ/8oJy3/GRgd/yIeJf8nIyn/JR8l/yUgJP8qJij/IBka/xYKDP8nHR3/MSQj/yQVEf81Ix7/NR8a/ygPAP8uEQ\
                D/c0w3/55xVf+jdVX/votp/4lbOP9mOxv/flEw/5FiQf+AUzT/eE4w/5RnSv/Lm33/3q+T/6p+Zv+AWET/hFxH/4ZeR/+IXkT/im\
                BE/4xhRP+SZUb/jWBC/5BjRv+RYkX/kGFD/5JjQ/+TYkH/k2JB/5NgQP+QWzz/lF46/5hgPP+ZYDv/mWA7/5phOv+aXzn/m2A6/5\
                pfOf+bYDr/ml85/5tgOv+aXzn/mmA7/5tgPP+aYDv/m2A8/5leOv+XXzr/lFw5/5ZgPv+dZkf/gU85/2A3Qv9gN2UAUzyCAEE3jQ\
                A5M5EAOjSSADo0kwA2MZMAMi+VADAulAAtLJYA////AP///wD///8A////AP///wA/O4IANDGDADw0fwBJPXX/bVpg/2pWXv9MNT\
                //Wz07/5NvXf+yi3P/p4Ns/5RxW/9TNiX/d1lN/3RbVP87KCT/HwwK/yYXFv8zIyP/KBsc/xwQEv8VCAv/KCAi/zAoKv8gGx3/Fh\
                EU/xsXHP8rJSv/JiQq/x4YH/8oJiz/JyMp/x4aH/8qJiz/Ix8k/yEdIv8vKiz/JB8h/xUKDf8iGBn/NCYm/ycVFP8wHRn/OiQf/y\
                sTAv8jBQD/Yj0m/4peQv+ldFT/uIVi/5ppRv92SCf/dkcl/5FgPv+PYD//jl8+/5ZnR/+PYkb/pXdd/86ehv/svKD/s4Zs/3RNNf\
                +AVz7/l2xO/45kRP+QY0P/lWhH/5ZnSf+WZ0n/kmNF/49gQf+LXTz/i1o4/49cO/+cZkX/lmA+/5hfPP+ZYDv/mWA7/5tgOv+aXz\
                n/m185/5leOf+bYDr/m2A6/5tgOv+aXzn/ml85/5tgOv+ZXjj/mV44/5pfOf+bYj3/mF86/5hgPP+eZ0T/i1Y4/2o8Nv9UMT0AVj\
                d3AEg7iQBAOJIAOjSTADkzkQA3MpQAMzCWADIvlQAyL5UA////AP///wD///8A////AP///wBmV2QAUEd4AEtAfP9qWF7/b1tj/6\
                yNq/+FaXL/Wjw2/4hkUv+thnD/o39o/6B8Z/9cPi3/clVH/3JYUP9GMC3/IxEQ/x8MDv8sHR//MiUl/xsPEv8ZDQ//HBMV/ycgIv\
                8vKSv/Gxca/xUMFf8lHyX/LSsx/xkUHf8kIin/KScu/xcWHP8kICf/Ix8l/yMdI/8pIyn/KCIk/xsTFP8WCgz/Kh4e/zEiIf8mFB\
                H/OiQf/y4VB/8iAwD/US4Y/4FWOv+te1r/toNg/6h1Uf+FVDH/az4c/4dWM/+aZ0P/jl07/45ePP+LXT7/il5C/51wWP+xg27/2K\
                iT/8ueiv+fdWP/fFVE/4BXRP99VED/dk04/3hPP/90Sjz/bUQ4/25FO/9lPTH/YDYl/3NELP+RXkT/l2FC/5piQv+ZYD3/mF86/5\
                tgOv+bYDr/m2A6/5pfOf+bYDr/m2A6/5tgOv+bYDr/ml85/5pfOf+ZXjj/ml85/5pfOf+hZ0L/nGM9/5hgPP+bZEL/jlk5/24+KP\
                9XLS//VzJjAEw5gABGPJQAQDmUAD02kQA4M5UANzKUADAulAAxL5UA////AP///wD///8A////AP///wByXlkAYU9u/21cZv98aG\
                7/noSX/9G1wP+cgIf/Wzw0/3lXRf+hfWj/oH1q/516af9yUkL/Z0k8/21RSv9ZQkH/LRka/xcAAv8nFxr/Nygs/yIUGP8ZDRD/Ew\
                UJ/yYeIf8zKy7/Hhkc/xMME/8cGB7/LCgu/yUhKP8eGSH/KiYu/yMfJv8gGyP/KSUs/yIeI/8gHCH/MCot/yMdH/8TBgj/JBka/z\
                srK/8gCgn/MxwY/y4WCv8oDQD/QB8K/3ZMMv+oeVn/r3xa/6t5Vv+LWjj/c0Ul/3xMKv+kcEz/lmRA/4pbOP+QYUD/fVI0/2tDK/\
                +DW0T/tIl0/9asmf/ht6n/rod6/4ZiV/92UEb/ck1B/187M/9aNzX/VTI5/1c1P/9WMjv/UCsu/181Lv98TTz/jFg9/5hiQ/+YYD\
                //lV04/5xhO/+cYTv/mV44/5leOP+aXzn/ml85/5xfOv+cXzr/nF86/5teOP+aXzn/ml85/5pfOf+fYz//mmE8/5JaN/+RWjf/jF\
                c1/3pIKv9nOSz/XDRd/0oycwBANYcAPzaOAD83jgA5M5EANTCSADMvkgAyL5UA////AP///wD///8A////AP///wB2YVgAb15l/4\
                JsbP/TvMf/5MnS/7ugqf+AZGf/XD80/2tKOf+ZdmH/q4d2/5VzZP99XUz/Vjkt/2ZLRP9uVFX/Oicq/xUAA/8hEhb/NSYq/ykcIP\
                8YCg7/EwcK/x0UF/8oIiX/LCYp/xgSGf8SCBP/JyAo/zArNP8VDxr/JSMr/ywlL/8WFBz/JyIr/yAaIf8gFyD/LScs/yYeIf8VCg\
                z/GQ0P/zkpKf8lEhH/LhgW/zUcFP8zGAf/MRIA/2xDKf+gclT/rHtc/7WDYv+dbEr/b0Eh/3NFJP+ebUn/lWVC/5VlQv+XaUf/cE\
                cq/102H/92Tzf/e1ZA/5x2Zv//1sn/9MvC/7GMhv+HZFz/ZUI8/1g3NABXOD4AUjVAAFQ0UABTNksAVDQ+AFkzNv9gNy//e0s0/5\
                VgRf+ZYUH/klo2/5thO/+eYjz/ml85/5leOP+bYDr/ml85/5xeOf+cXzr/nF45/5pdOP+bXjn/m2A6/5leOP+cYDr/lVs3/4xVMP\
                +LVDH/jVg0/4dTM/9+TDf/ZENX/1U0cf89MHwAPDSJAEM5jQA9NpEAOTORADgykAA1MJIA////AP///wD///8A////AP///wB4YV\
                b/e2Vh/8SutP/p0s//6NHZ/6SFp/9iTlX/Szc+/1M8Q/+KbWr/r4x8/557aP+Qb13/YkQ2/2VHO/94WVH/UTYu/ykUE/8uGx7/Ny\
                cs/zElLf8bDhT/FAgM/xMFCv8lHCP/NzA1/xoRGf8HAQ7/IBsl/zArN/8cFyH/JiAr/yolMP8aFR//KCIt/yYhKv8gGSH/IBoe/y\
                skKP8eExb/FgMI/y8fI/8uHCD/Lxkb/0EmJP8/IRf/QyIO/1AtEv+VaEn/p3hW/7mGY/+peFX/f1Ex/2o/IP+KXDv/mGhG/5NmRP\
                +JXDv/Zz4g/2tCJv+DXD7/dlE6/5ZvWv/wx7X/+9PG/82on/+TcWv/ZEdJ/1Q8SABVOmAAVDtsAFc7cABYOm4AWDhpAFs1WgBPMD\
                3/ZTs8/4ZURf+XYUL/mF86/5phPP+bYj3/mGA7/5hdN/+bXzn/m2A6/5pfOf+bYDr/ml85/5pfOf+aXzn/mV44/5leOP+ZXjj/kl\
                o1/41WMf+OVjL/klw4/5VfPf+VX0H/hlVL/2dASv9aM2IARTiBAD42jQA+N5IAPjeVADo0kwA4MpEA////AP///wD///8A////AP\
                ///wB4Ylb/hHF2/+HLz//p0s7/6NLY/4l2fv9qVVf/SDU//0czPv9wVFb/oH5s/66Jcv+tiXT/e1hF/2ZFNv93Vkn/akxC/0kwLv\
                87Jiz/Pi00/z4uPP8tHS7/Hg4e/xkLF/8nHSj/NCo2/xwTIP8QBhj/HRcl/zAnN/8lHy7/Jh8v/ykiMv8fFif/KCEw/ywlNP8kGy\
                n/JRom/zIoMP8nGiH/IBEW/y8gKf89KjH/Qy0y/0YsKf9WNyz/a0cz/2I8Iv90TC3/nXFR/7uLaP+xgV//lWdF/2lAIP91Sir/l2\
                tI/5ZqR/9xSSj/Xjka/3pTNP+HYUb/gV5J/6iCcP/owrP/48C4/9Kwqv+fgH7/ZElQ/1E3TgBSOGIAUjpuAFE6cABVOW0AVDhtAF\
                g3ZABXNFIAVjI7/21BPf+HVDz/mWJA/5tiP/+UXDn/klo2/5lgO/+bYDz/ml87/5tgPP+aYDv/mV46/5leOv+ZXjr/mV44/5pfOf\
                +ZXjj/lFw3/5JaOP+UXDn/ll87/5hiP/+bZET/kmBH/3lMR/9bOkz/VDZyAEM4hgA7M4sAPDWQADo0kwA5M5IA////AP///wD///\
                8A////AP///wB4YVf/kH+F/+TOz//p0s7/6NLU/4Nubf9uWVv/UTtZAEgxUv9KN0X/dlpU/5p6av+efXH/eFlP/10/Nv9jRkD/bV\
                JT/1dBSf9LNEv/SjZT/0o5VgBDNlgANSpNACsjQgAyK0cAOjFNACsnQQApHzsAKiQ7ADwyRf89M0X/Mi5G/zk0UP8sKUX/LypI/z\
                YwTP8zLEf/MyhA/0IzSf9BMUn/OyhE/0UvSv9KNkL/Ujg//04wL/9mRTv/jWZS/4VcQv9hOx7/gVg5/59xUv+md1X/i18//29FJ/\
                9jPR7/fFMy/3pRM/9eOBv/aEMm/41lSv+CX0b/bk47/6eFd//uyr7/58fC/96/vv+ojI7/ZExU/1A5WQBPO2kASjx0AEo8dABRPX\
                YAUDt2AFc5cgBePGoASys2AFw2Pf95Sz7/lF9F/5tkRP+TWzj/lFs3/6BnQf+bYj3/mmE6/5tgPP+aXzv/mV87/5lfOv+ZXzr/m2\
                A8/5tfOv+WXjn/l187/5deO/+WYDz/l2E//5hiQP+aZUT/kmBD/35PQf9fOkT/WjReAFI4dwBDOIYAOTOOADo0kgA3MpQA////AP\
                ///wD///8A////AP///wB4Ylb/lYKI/+bPz//p0s7/6NHT/4Ntbf9rV1sASztmAEQ7dABCN2j/TzlV/1RBSf9dR1H/XEZQ/0w3Rv\
                9HMET/UDdW/0o4Yv89NGj/ODR0AD04dAA5NngAMDB2AC0ucgAxMXQANjZ2AP///wD///8ARjxXAGBRU9FnVVPRYFFU0To4bwA1NG\
                oAMTFrADk3bQA6N20AOjZpAEI8awBEPWwAQjlpAE89ZwBbP10ATDZAAGRCOf9rRzb/gVpB/4ddQP9pQiX/aUIi/2lCI/9mPyD/bE\
                Um/2tEJf9cNhj/XjgZ/2A8Hv9hPR//d1A1/4ljR/+LaFH/aUk4/5l6bf/vzcL/6crI/9i6uv+mi4//YEtS/043WABLPWwARzxzAE\
                o8dgBNP3kATD14AE46dABTOXAATzFpAFgyXgBbOUb/c0lP/4tZTf+VYEj/lF9A/5ZePP+bYj3/mmE8/5phPP+ZYDv/mWA7/5dfOv\
                +YXzr/mWA7/5lgO/+ZYTz/mF88/5ZgPf+WYD7/lmA9/5ZiQf+YZET/lWJE/4FTOv9nPjr/UzNBAFo5bQBJO4UAODKNADMwkgA0MZ\
                MA////AP///wD///8A////AP///wB4Ylb/k4KH/+XP0P/p0s7/59HT/4Jtb/9pVlsAPTRjAEY9dgBHPW0ATDdP/0g1O/9CLjr/UD\
                pK/1M6T/9MMU7/SDBW/0Q3aQBBOXcAOjZ/AD46fAA1NH4ALTGCADE0hgD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8ANTd+ADY2fAA2NXwANzZ9ADs3eQA8N3YAQztyAEw6ZABNNUgATDE4/2dFOv+BXEf/jGRJ/41kRv9/WDj/eE8x/31UM/\
                +CWDj/flU0/35XNf94UTH/eFEw/4BbO/+KY0L/jWlJ/5FtUP+FZEv/cFJC/5t7bv/qzML/5MjF/9C1t/+ki5D/XklR/045WgBMPW\
                oARzxzAEg+dwBMP3oASz16AEk6dgBNOXMAXz9tAF04XwBOLz4AWzU4/3tMPf+ZZUX/nmZC/5FbNf+WYDr/mWI8/5dhO/+ZYDv/l1\
                88/5deO/+YXzz/mWA9/5lgO/+XYDz/lmA8/5ZgPv+VYT7/lGE//5VhQP+UYkL/kF8//4JTN/9rQS3/WTU5/1A0Rv9NMWYANC19AD\
                AtiwAzMJEA////AP///wD///8A////AP///wB4Ylb/koCF/+XPz//p0s7/5tHS/4Nvcf9qWl8APTdwADk2fwA4NX4AQjt0AE1Ccw\
                BGO20ARTpt/0Q8c/9IPncAQzt7AD45ggA+OYUANDOGADY1hAAvMIUALzGIAP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////ADo4eAA5N3sAOzl9AD06eABCO3QATDxkAE02SgBYPED/dlVK/4hiUP+SalL/iGBE/4hgQP+Ua0r/jm\
                VD/4tjQf+GXDv/jGRC/4ZePP+JYT//iWNC/41nRv+PaUn/iWVJ/4tnTv+EY0n/eFlI/5l8b//pysH/6s7O/9m+wP+tlJn/YU5V/1\
                Q+XQBOPmYARzxvAEU9dABKQHkASz98AEs9egBMPXgAUECAAFM+fgBWNm8AVDFPAGE6Q/+BUkP/lmJE/5ZiPv+WYD7/l2E9/5dhPf\
                +XYT3/l2E9/5dhPf+YYTv/l2E7/5hhO/+YYTv/l2E9/5VhPP+WYj//l2I//5VjQf+VY0H/lmRB/5NiQf+KXD//g1dC/3BKSv9YPE\
                7/UzZrAEo6fQA5NJEA////AP///wD///8A////AP///wB5Ylb/k4CF/+bQ0P/p0s7/6NLS/4NvcP9oWFwAOzVrADY1fwA1NYMAND\
                N+ADg1gAA3NogAMDKFADAwhwA0NIoAODaJADY1iAAyM4cAMjKEAC8whQAtMIcA////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////ADU1fAA2NX8AODd9ADw4eQBBOnAASzhdAEw2PgBqTET/j2pV/5pwU/+VbEz/k2pI/5pwTP\
                +acEz/mm9L/5txTP+dck7/lWtJ/5JpRv+VbUr/l29M/5BpSP+Oakr/jGhJ/45sUP+Ka1D/dllG/5x/cf/kyL3/4sjF/93Fxv+0nq\
                L/ZlVb/046VgBGOWEARDxtAEY8cQBDO3UASD54AEo+ewBKPXgARzt5AE48egBPOnUAVjNaAFEtNv9sQS//i1o6/5pmQv+WYj3/lm\
                I9/5ZkPv+YYz7/lmI9/5ZiO/+XYDr/lmI7/5ZiO/+WYjv/lWA6/5VjPf+UYj7/lGI+/5NjQP+TY0D/k2NC/49gPv+TZET/l2hM/4\
                hcRv9rR0r/VztO/1c4ZQA6NYsA////AP///wD///8A////AP///wB5Ylb/mIWJ/+fR0v/p0s7/59HR/4Jub/9pWF0APDZoADg3ew\
                A4N34ANDV+ADEygAAxMoYAMDKJADAyjgAwMo0ALTCLAC4wiAAxMYcALzCFAC8xiAD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////ADc2egA0NX4ANzZ9ADs3eQBCOm4ASjRTAFM7QP9xUT7/imRH/41mSf9/WDj/iG\
                A+/4tkQP91UC3/glw4/4dgPv+DXTv/h2A8/31XNf9+Wjf/imVC/4RgP/95WDj/eVg6/3paP/9sTzX/Y0o2/6OHef/my8L/4MfE/+\
                XPz/+4par/Z1Vc/0s6VQBEOF4AQzxsAEc+cQBDO3UAQjt3AEc+ewBLPnkASTt4AEc7eQBNOncAUTJfAFAwOv9vRTT/i1s7/5JgPP\
                +TYT3/k2E9/5JhPf+SYDr/kV85/5RgO/+VYTz/lmI7/5ZjPP+UYjr/k2E7/5ViPf+UYj7/kWE+/5BhPv+PYD//lmZE/41ePf+MXz\
                //k2ZH/4peRf9yTEX/Wj1H/1U2VAA/Nn8A////AP///wD///8A////AP///wB5YlX/moeH/+fR0f/p0s7/59HR/4NvcP9rWV0APj\
                dnADU0fAA1NYMANTZ/ADQ1fgAyMoQAMTOGAC4xhwAxMYgALzGJAC8xiQAtMIsA////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wAzNH0ANTV8ADw5eQBGPnQASzphAEw5Qf9jRTz/cU80/2JCJv\
                9ePCH/Xz4k/189JP9hPyT/Xjwg/1o4HP9aOh3/Xjwf/2JBI/9ePiD/a0wu/2ZIKv9fQiX/XUMo/1xCKf9SOib/WEAw/6CHev/u1c\
                v/3MS+/+PNzf++qq3/Y1NZ/0s6VABLPFwAST5nAEc+agBGPm8ARz5zAEc9dwBHPXsAQzt/AEQ6fABNOXMAVzVbAFk2Pv94TTr/km\
                NB/5RkP/+TYjz/k2M+/5NhPf+SYDr/lWM9/5ZkPv+XZD7/mGU//5pnP/+TYTn/kWA6/5hnQv+XZkH/kWE+/41gPv+RY0H/kGND/4\
                xfPf+IXDr/g1g8/3pQO/90TUT/YUJM/1IyWgA/NnoA////AP///wD///8A////AP///wB5YlX/loOD/+bQ0f/p0s7/59HS/4JvcP\
                9qWFwAPDdoADM0fQAyNIIANzaAADQ1gQAuMoYALzKIAC0xigAwMYoALzGJAP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wAzNH0ANTR7AD45eABDPHUATT1nAFZBU/9eRD7/ak\
                w3/21LLf9xTzD/elc4/3ZUNv91UjP/dVM0/3VSMv92VDP/b04t/3hXN/97XDv/e1w9/2lNLv9ZPyL/Ykgu/3pfR/9rVEH/Y009/5\
                V9cP/jysD/3cbC/+rT0/+4par/ZlZb/2NOaABWRGUARTpjAEU9bQBFPXEARD12AEQ9egA/OHsASTtzAE06bgBXOWEAVDhCAGdBO/\
                +IXD//m2xG/5NjPP+XZkD/l2Y//5RjPf+TYzz/lmY//5ppQv+UZD3/kWE5/4pbM/+TYzz/jl84/4lcN/+RY0D/jmE9/4JYNv+FWz\
                j/jWI//4ZbOf9/VTP/gFc4/4BYQP9uSTv/WTpC/1U0VQBOOmsA////AP///wD///8A////AP///wB5YlX/lICA/+fRz//p0s7/6N\
                LQ/4Rwbv9tWloAQzxmADY1eQAzNIAANjeAADI2hgAxNIYALjKGAC8xiAAsMIgA////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wA2NH8ANjR8ADw3dQBGPW8AWURnAGZPVv\
                99Xk3/jmxN/6J9Wv+rh2T/tI9s/62IZv+og2D/q4dj/66IY/+ui2b/r4xn/6qHY/+ffVv/l3hX/4ZqSf93XUD/eF5D/5d8Zf+lin\
                L/f2ZR/5R7aP/nzcD/5c3K/+DLzv+rmZ7/cmFm/2ZUcgBVSG8AQTptAEE7dgA6NXQAPzh3AEA7gQBAO4QATEKDAEM6ewBJOHAAWT\
                pYAGdGR/+DWUP/j2JA/4teOP+OYjz/jWE7/5BkPv+OYjz/il03/4ZZNP+EWTL/gVcv/31TLP+AVS7/fVMu/3RLJv9sRCH/cUkn/3\
                ZPLf90Ti3/dE4t/3pTMP95UjH/fVY5/3xWPf9nRTj/TjI5/1E1UwBCOH0A////AP///wD///8A////AP///wB5YlX/loKA/+fR0P\
                /p0s7/59HQ/4Jvbv9oWFwAOzVkADMzdgAxNHoANDZ9ADEzgQA0NYEANDWCADAzhQD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wAzM4EANTR/ADw3dgBFOWYAX0\
                dh/3dcW/+cemP/t5Bu/8Cadf+/mXT/vJdy/6qFYf+beVP/m3lT/5l3Uf+XdlD/nHlU/5V2Uv+Wd1X/m35c/5x/X/+KcVL/clo+/4\
                JqUf+PdV3/emFK/5N5Y//ix7b/5czD/+rSzv/DrKf/gGtk/2hWXABcSF0ATD9gAEtAagBJQG4AR0BzAElBdwBIP3gASkB5AEg6cg\
                BMNGEAVThQAGdHTf+BWkr/jWNG/49kQf+RZkX/hVs6/3lQMP9sRCX/Yzwc/2U+G/9xSib/eVIs/3VOKP9gOxb/XTkW/1w4Ff9ZNR\
                T/ZD8f/25JKv9hPyD/ZUAi/29JKf9tRyn/Yz8k/2RBLv9rSkD/ZElQ/19CZAA/NXAA////AP///wD///8A////AP///wB5YlX/l4\
                J8/+fRz//p0s7/59HP/4Nvbf9rWlwAQTtkADc2dgA0N34AMzZ/AC80gwAxM38A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wA3NnoART5zAExAZg\
                BUPVoAYUtS/4dnX/+tiGv/w5t3/7+ZdP+1kGv/rYhk/6B8Wf+deFP/nXtV/5x5VP+aeFL/nHpU/55+Wf+ef1z/oYNf/52AX/+Rd1\
                j/gGhL/492Xf+Mc1j/gGZM/6OHbf/oy7f/4Me8/9vEwf/Fr6v/h3Fq/2NSWABYRlwASz1jAEU+cQBBOnMAQj17AD85ewBCO34APj\
                h+AEU9gQBJPXYAUjVYAFg5P/9wSjf/dk0u/2pCIP9gOxj/XzsY/2dBIP92Ty3/f1cz/4tkPv+QaEL/jGQ8/4ZhOP94VS3/ZkQf/2\
                5LKP+GXzv/kGtH/4hkQv+AXT3/dlEx/3ZRL/9uSin/Yz4i/2dFLP+CX0//fl9g/11GUv9KNWAA////AP///wD///8A////AP///w\
                B5YlX/lH55/+fR0P/p0s7/59HQ/4Rxb/9rW14APTllADQ1dgAzN38ANzh8ADU3fgD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wA6OYAAQj\
                11AE4/ZABTPVIAZk5T/5JyZP+0j27/wJdx/6+JZP+lgFv/n3tX/5p2Uf+deVT/oH5Y/517Vf+celT/mHZQ/5p4VP+VdlT/l3pW/5\
                6BXv+hhmX/noRm/6qQc/+ojHT/eWBL/5N5Zf/nzL3/7dPI/+bNxv+2npX/dl5W/2ZPSv9WREn/TDtVAE9CawBKQHEASUF3AEY9dA\
                BDPHkAST1tAFU/bABYPl8AVT1F/2NEPf92UDn/f1k1/35YMv99VzT/f1k2/4ZgPf+QaUb/mnJN/6F6VP+jfFT/nXZP/5l0Sv+Wck\
                j/kW1F/4dkPP+CYDr/iWdD/5h0T/+jflv/lG5L/49qRv+Rakf/jWZE/4xmRv+cdVn/lHBg/2xPUf9dREz/////AP///wD///8A//\
                //AP///wB5YlX/kHt3/+fR0P/p0s7/6NLS/4NwcP9oWFwANDFkACgueAAnMoIA////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                AyNooAMTJ/ADk1cABJN1cAXEdO/5Fzav+zj3L/sIpm/5t3Uv+WdU//mXdS/5x6VP+ffVX/ooBa/6F+Vv+hflj/qodh/6uKYv+igl\
                3/p4lk/6KFYv+Ve1r/g2pM/3lhRP9vVj7/Y0s3/5d+a//lyrv/4Ma7/+/Wz/+vlY//fWZi/8mvqP+Tf4T/SzlWAD42ZwA+OHQAPT\
                h6ADMwdgA8NnwAPTd6ADozdABJOGcAW0VS/3NVT/+GY0j/mXNN/6uDW/+2j2b/to9m/6uGXv+fe1T/nXhS/6B7U/+kflb/on5T/6\
                J9Uv+jfVP/qYNY/5dySv93VTH/dFMu/5BtSP+rhWD/on1Y/597VP+jfFb/pX5X/6J5Vf+mgF3/n3hd/4ZjVf9jSVH/////AP///w\
                D///8A////AP///wB5YlX/k311/+jRz//p0s7/6NLQ/4NvbP9qWVgAQjtdADc3dwAyNXoA////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8AQTttAFA8WwBMO0IAYElH/5R2Yf+0kXD/qIVf/6KAWP+nhFz/q4hg/6aDW/+ffFX/oH1V/5l3UP+aeFD/l3VO/5\
                h4Uf+Ka0f/jG1J/35iQP95Xj7/g2hJ/4htUf+BZ03/a1M//56Ecf/jyLj/3sO1//vdz/+hh3v/iG9k/+rLtf+tlJD/RTQ+AEk5YQ\
                BMQ3cARDxzAEM8eQBFPX0ARDt2AEg7bwBYPmAAaE1U/4dnWf+he1r/upFo/8qidv/FnXP/wptx/6+JX/+deVL/n3pT/6B9U/+ffF\
                P/nXpP/6J8Uv+ifVL/nnlP/514UP+Vc0r/fl44/35eOP+celT/o39a/6eCW/+og1z/qoNc/6qDXP+lfVn/j2hL/3dVQ/9jRk3///\
                //AP///wD///8A////AP///wB5YlX/lX50/+jRz//p0s7/6NLP/4NtZP9yXVMAcl5UAHdiVAD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8AdlpIAHVbSAB1WEP/Zkoy/4hpS/+belj/ooBc/558WP+beVP/nXtV/5l3Uv+Rb0j/i2pF/4lqQv99Xz\
                j/dFcw/3JXMf9sUi//c1g1/4RqR/+kiWj/tJh2/+3Prf/32rv/p45z/4RrVf/w0rz/5cm3/+zPwf+3mon/eF1H/4tsUf94WTwAaU\
                wvAHhaPwB8XkQAfF1AAH5dPgB4WDoAfVs4AIFdOAB7VzEAbksm/49pQP+6k2j/wptx/8Kbcf+zj2P/on9W/6F+VP+hflX/nntS/5\
                18Uv+fflT/nHtP/5x5Tv+ceU7/m3hN/598Uv+mgln/m3ZQ/5NvSf+gflb/oXxX/5h1UP+ZdVH/lXFL/4xnQv+GYTz/fFYx/3NOKf\
                92US7/////AP///wD///8A////AP///wB5YlX/mIJ5/+nSzv/p0s7/6dLO/4ZvY/95Y1QAmH9pAP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8Ao4JdAKyLZgCtjWn/fmA9/3FVMv9zVjP/elw5/2hNKv9uUS//clUy/3pdOP+BYz7/i2xG/5\
                V1T/+afVX/o4Vd/6+PZ//Ao3v/2LqT/+jMpv/94bz/5cml/+TJp//dwKD/mH9l/452YP/ozLf/4ca1/+zSx/+9opb/dVtL/3FUPA\
                CTc1QAnHtZAKmGYQClglwAp4RaALGNYQC5k2UArIZbALOMYQCfek4Aflow/45oP/+4kmj/upNr/6B7VP+ZdU//lXNM/5t5Uf+de1\
                P/mHhQ/5t6UP+fflT/nXxS/518UP+dfFD/n35S/55+U/+hgFX/q4pf/6eGXf+Pb0f/iWhB/4JhO/94WDH/e1ky/3tZMv+QakP/pn\
                5W/5pyS/96VCv/////AP///wD///8A////AP///wB5Ylb/n4mE/+nSzv/p0s7/6NHP/4JsYv////8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8AwKKCAMKkhACzk3L/k3VU/4JmRf+IbEv/k3ZV/5V2Vf+ZfFr/nH5b/6aIZP+9nn\
                f/zq2G/9++lv/z0aj//+G3///lu///88r///DI//XZtP/jyKP/sJd2/5R8XP92XkD/aFE3/5mAZv/v07r/6c24/+nNvf+3nIn/c1\
                hD/7eVdgDOqocAwJx4ALeUcQC+mnYAxZ96AMKbcgC7lGwAwJlvAMSccgCshVoAhWI5/49rQv+7lGr/tpJn/5VzSv+de1H/n35U/6\
                KBV/+ff1T/m3tS/59+Vv+ig1j/nX5T/6WFWP+Zek3/j3FH/5J0Sv+SdEn/gWQ7/3ldNv+EZj//iGlC/5JzS/+Ob0f/oX5W/7iTaf\
                /ku4///+G0//DGmv+OaD//////AP///wD///8A////AP///wB7ZFb/sZuQ/+rTz//p0s7/59HO/4JuZv////8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////ALOXfACuj3QAk3Va/5l9Yv/rzK7///LU///qxv//6cP//+jC//\
                /xyP//+dD///bL///wxv//8sf//+3D//DQp//Lrof/oIRf/3JaOf9tVTT/b1c4/4ZsTACWeVkAfGJE/52BZv/py7L/4MSu/+jMuf\
                +zl4T/eV9K/6SDZgDAnHsAuJVyALKQbgCzjm4Aso1qALaQbAC6lXAAu5VxALmTbQChfFUAg2A5/4hlPv+lgVb/rIhe/5t6Uf+ce1\
                H/mXpQ/5l6UP+Yek//nX5T/5+AV/+ae1H/knRK/5J0Sf+Udkv/im1D/4NmPP98YDn/cVUu/3dbNP+Rc0v/uppy/9u3jP/20qf///\
                LE///0x///8sb//+/D//bMov+PbET/////AP///wD///8A////AP///wB5YlX/vKOa/+nSzv/p0s7/6dLO/5aGg/////8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AKiMbgC3mXkAq45t/4ZrS//Epob/+tm4///10P//6s\
                P//+a+///ju//uz6X/zrCH/62QZ/+ZfVX/fGA6/3ddN/99Yz7/iGxH/4tvTACRdVEAnX9dAMChfgCzlXQAfmRG/5B1WP/uz7L/38\
                Ko//LVvP+3mH//dltA/6uKagC+mHUAt5JtALiSbgC2kWwAuJJsALmSagC0jmYAu5RrAL+WbACogFYAiWY8/4ViOf+Ma0L/lnRL/5\
                h4UP+Sc0v/jm9H/4dqQv+EZz//fmI6/3dbNP9uUyv/aE0l/1Q7FP9pTib/iGtB/51/Vv+0lGr/372R///htP//57r//9yx/+fDmv\
                /EoXf/tpRr/6eEXP+QbkX/iGU9/4hlPf9/WzQA////AP///wD///8A////AP///wB7Y1z/uaKd/+nSzv/p0s7/5s/M/5qHg/////\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////ALKWegCtkHEAu517/5J1VP+McE7/pYhl/5\
                6BX/+VeFX/mn1Z/5+BXP+WeFP/im1H/4doQ/9/YTv/f2E8AItsRgCVdk8ApYVgALmYcgC6m3YAtZZxAMmqhAC9nngAg2hH/5t/Xv\
                //3rz/6Meq//fWu/+/oIT/f2BD/6uHZgC+mHQAuZNsALiSawC3kWsAu5VuALyUbAC5kGkAupFoAMOccAC2j2QAkW1D/3ZVLP94WD\
                H/gGI5/3xeNf98Xjf/fmI6/4lsRP+Udk3/mHxS/6GEWv+wk2j/tpht/9GyhP/jw5T//dys///ktf//3K3/8M2h/9m3jP/CoXf/tp\
                Zr/6GAVf+LbEP/hmU9/45rQ/+Pa0H/g142/4lkOwCfeE0A////AP///wD///8A////AP///wCEbF3/vaSX/+zVz//p0s7/6tPO/4\
                x7c/////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wC+noEAsJFyAKeHZwCZel\
                v/gmVF/4FjQf9/YUD/gWNA/4dpRf+MbUcAmXdSAKmGYAC0kGcAvZlwAMGccwC9mXEAtZFrALqWbwC3lG4AsZBqALmXcQC0k20Aim\
                tH/5R1VP/atpf/5sOp/+jGr/+5loL/gWJL/6N9YAC+lnQAuJBrALmRawC7km0AvJNsALqRaAC5kGcAs4phALyTagC7kmkAnHdN/4\
                hlO/+siFz/17KE/8ejdf/IpHb/yqh8/9y6jf/qyJn/99Sl///mtv//9sX///jH///zw///7r7/99Sl/9Wzhv+9nHD/ooNY/4NkO/\
                9yVCz/elwz/45tRACohVsAr4leALeQZADFm3AAxJtvAMaZbQDEmm0A////AP///wD///8A////AP///wCBaFX/tJ2N/+nRxP/fyL\
                7/zriv/1tLRP////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AL\
                iXdwCtjWsAro5sALaTcAC4l3MAtJNtALOSbAC3lm4AtJBpALSQaAC7lm4AvZduAL6XbwC5k2sAso1nALeRawC4lG0AuJRtAL2Zcg\
                C3km8AoX1dAIVkR/+Rb1P/wp6C/76afv+efF//jmxN/6uDXwDEmnMAuI9oALiQaAC8k2wAu5JrALeNZgC+k2wAvpJoAL2UaQC9k2\
                gAonpQ/4tnPv/XsYP///fH///tvP//8sP//+2+///xwf//88P//+u7///ouP/61qf/2riK/9Cugf+bfFD/d1ow/3JWK/92WC7/i2\
                tA/6aFWgCxjWIAuZRoALiRZgC+lmoAupNoALKKXwC5kGUAvZFlALuPYwC+kmYA////AP///wD///8A////AP///wCWe2L/k3lj/6\
                +WgP+ZgW7/bltN/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AMKhgAC9nHkAupl3ALqZdADDoXsAvpp1AMWgeADEoHgAvppzAL6YbwDAmXAAuZNrALmTawC8lW0AwJlxAMGacgC+mHEAup\
                RuALaQagDCnHUAv5ZwAKeAWwCUb0n/lG5J/5RuSf+Zc03/sIZgALeNZwDAlW4AxJhyAL2SaQC9kmkAxJhwAMOXbQC7j2UAu5BmAL\
                +TZwDJnHAAqYFV/4xnPP/AmGv/8sqb/+G6jP/lv5D/5cCR/9m1hv/FoXT/roxf/5Z1Sv+Jaj//j29E/5BwRf+PbUP/jWtB/557UA\
                CwjGAAso1hALaPZADJoXQAxJ1xAMCYagC/lWgAwJZpAMOZbAC9kWUAvJBiAMSXaQDDlWcA////AP///wD///8A////AP///wCdgm\
                kAiW9YAIt0YQB4YlEA////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wCti2wAqohnALKPbACyj2oAr4xnAKuFYACyjWcAvZZwAL6VbQCvh2AAuJBpALaNZgC0jGUAt49oALqRag\
                C+lW0AvZRtAMCVbgC0i2QAwZhwAL+WbQCyiWEAqoJZAKR6UwCrgloAw5dvAMGWawDClmsAv5JoALuOZAC9j2YAwJJoAMCUZwC/k2\
                cAwJJmALqPYwDBlWkAt4xgAKB4Tf+hek7/poBT/5RvRP+RbkL/mHVL/5x5Tv+Wc0n/jGpA/4NiOP+LaT//l3VKAKaDVwCsiFwAtJ\
                BkAMGabgDMpHgAw5tvALaQZAC8k2YAu5FkALuRZQC7kmUAvpJmAL+TZwC9kWMAu49hALyQYgDDlGcA////AP///wD///8A////AP\
                ///wB9Y0sAg2xWAHpkUAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8AkXJVAINkRAB8XDwAhWVCAIRiQACFYz8Ag2E9AIZiPgCFYT0Ah2I9AIZhPACJZD8AjG\
                dCAJJtRwCZcUwAl29KAJZuSQCXb0gAmnFKAJpySwCcc0wAnXRNAJtzSgCYcEcAmXBIAJ90TACab0cAmW5GAJtwSQCccUcAm3BGAJ\
                pvRgCab0UAm3BHAJRrPwCXbkIAoHZKAJ10SP+FYDb/dVEo/3JQJv97WC7/dFIo/3VUKv+AXzQAjWtBAJl3TACdek8AnXpPAJRwRg\
                CbdkwAmXRKAJVwRACXckYAl3BFAJRtQgCac0cAk2xCAJdwRQCacUcAmnFGAJhvQwCbckYAm3FFAJZrQACbb0IA////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///\
                8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//\
                //AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP\
                ///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///w\
                D///8A////AP///wD///8A////AP///wD///8AlGViLg=='
        _img=pickle.loads(b64decode(_data)).convert('RGBA')
        self.im = ImageTk.PhotoImage(_img)
    
    def gameEnvInit(self):
        self.randomIconPos()
        self.IconDatas()
    
    def Tips(self):
        messagebox.showinfo('Tips','使用前请右键桌面-查看，取消"自动排列图标"与"将图标与网格对齐"勾选,完成后点击确认。')
        self._showDesktop()
        time.sleep(1)
    
    def _showDesktop(self):
        win32api.keybd_event(0x5B,0,0,0)
        win32api.keybd_event(0x44,0,0,0)
        win32api.keybd_event(0x5B,0,win32con.KEYEVENTF_KEYUP,0)
        win32api.keybd_event(0x44,0,win32con.KEYEVENTF_KEYUP,0)
    
    def saveIcon(self):
        self.ICON.updateIconsInfo()
    
    def loadIcon(self):
        self.ICON.recoveryIconsPos()
    
    def gameDestroy(self,*event):
        self.root.destroy()
    
    def destroyTrigger(self,*event):
        if not self.ICON.recoveryState:
            self.ICON.recoveryState = True
            self.loadIcon()
    
    def randomIconPos(self):
        icons_list=self.ICON.getIconsName()
        for icon in icons_list:
            _maxloop=1000
            while True:
                pos=[random.randint(0,self.screen_width-65),random.randint(self.screen_height//2,self.screen_height)]
                if pos not in self.temp_icon_pos.values():
                    self.temp_icon_pos[icon]=pos
                    break
                _maxloop-=1
                if _maxloop==0:
                    break
            self.ICON.moveIcon(icon,pos)
        
    def IconDatas(self):
        _icondata=self.ICON.getIconsInfo()
        self.IconData=[]
        for i in _icondata:
            self.IconData.append(ICONDATA(name=i,id=_icondata[i][0],pos_x=_icondata[i][1][0],pos_y=_icondata[i][1][1]))
    
    def DrawBasicPlayer(self):
        self.Board.create_image(self.screen_width/2+24,self.screen_height//4-9,image=self.im,tag='player')
        self.Board.create_rectangle(self.screen_width*3/4-20,self.screen_height//6-50,self.screen_width*3/4+270,self.screen_height//6+60,tag='player',outline='#FEFEFE',width=3)
        self.Board.create_text(self.screen_width/2+24,self.screen_height//4-90,text='左键出钩↓右键退出',font=('微软雅黑',13),tag='player',fill='#CCCCCC')
        self.updateText('得分：0')

    
    def updateText(self,text):
        self.Board.delete('text')
        self.Board.create_text(self.screen_width*3/4+50,self.screen_height//6-100,text=text,font=('黑体',22),tag='text',fill='#FEFEFE')
        
    def HookActive(self):
        if not self.HookOrder:
            self.angleChange()
            
            self.Board.delete('lines')
            self.Board.delete('Hook')
            lineHead_x=self.screen_width/2+self.line*math.cos(math.radians(self.angle))
            lineHead_y=self.screen_height//4+18+self.line*math.sin(math.radians(self.angle))
            self.Board.create_line(self.screen_width/2,self.screen_height//4+18,lineHead_x,lineHead_y,fill='black',width=3,tag='lines')
            leftpos1,leftpos2,rightpos1,rightpos2=self.getHookPos((lineHead_x,lineHead_y),status='open')
            self.Board.create_line(lineHead_x,lineHead_y,leftpos1[0],leftpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(leftpos1[0],leftpos1[1],leftpos2[0],leftpos2[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(lineHead_x,lineHead_y,rightpos1[0],rightpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(rightpos1[0],rightpos1[1],rightpos2[0],rightpos2[1],fill='black',width=3,tag='Hook')
            if self.HookOrder:
                self.HookMove()
            else:
                self.root.after(20,self.HookActive)
        else:
            self.HookMove()
        
    def HookMove(self):
        if self.HookOrder:
            self.lineChange()
            
            self.Board.delete('lines')
            self.Board.delete('Hook')
            lineHead_x=self.screen_width/2+self.line*math.cos(math.radians(self.angle))
            lineHead_y=self.screen_height//4+18+self.line*math.sin(math.radians(self.angle))
            self.Board.create_line(self.screen_width/2,self.screen_height//4+18,lineHead_x,lineHead_y,fill='black',width=3,tag='lines')
            leftpos1,leftpos2,rightpos1,rightpos2=self.getHookPos((lineHead_x,lineHead_y),status='open')
            self.Board.create_line(lineHead_x,lineHead_y,leftpos1[0],leftpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(leftpos1[0],leftpos1[1],leftpos2[0],leftpos2[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(lineHead_x,lineHead_y,rightpos1[0],rightpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(rightpos1[0],rightpos1[1],rightpos2[0],rightpos2[1],fill='black',width=3,tag='Hook')
            
            self.TriggerPos=self.getTriggerPos(15)
            _ret=self.checkTrigger()

            if _ret==-1:
                self.HookBack()
            elif _ret:
                self.HookCatch(_ret)
            else:
                self.root.after(20,self.HookMove)
        
    def getTriggerPos(self,offset=15):
        _triggerPos=(self.screen_width/2+(self.line+offset)*math.cos(math.radians(self.angle)),self.screen_height//4+18+(self.line+offset)*math.sin(math.radians(self.angle)))
        return _triggerPos
    
    def HookOrderTrigger(self,*event):
        self.HookOrder=True
        
    def IconCatched(self,_icon):
        _randomX=random.randint(self.screen_width*3/4+20,self.screen_width*3/4+230)
        _randomY=random.randint(self.screen_height//6-5,self.screen_height//6+15)
        _icon.movePos((_randomX,_randomY))
        self.ICON.moveIcon(_icon.name,_icon.posOffset(_icon.pos))
        _icon.TouchAble=False
    
    def HookCatch(self,catchIcon):
        if self.HookOrder:
            if self.lineChange(1):
                self.HookOrder=False
                self.IconCatched(catchIcon)
                self.HookActive()
                self.score+=100
                self.updateText(f'得分：{self.score}')
                if self.checkWin():
                    self.gameWin()
                return
            
            self.Board.delete('lines')
            self.Board.delete('Hook')
            lineHead_x=self.screen_width/2+self.line*math.cos(math.radians(self.angle))
            lineHead_y=self.screen_height//4+18+self.line*math.sin(math.radians(self.angle))
            self.Board.create_line(self.screen_width/2,self.screen_height//4+18,lineHead_x,lineHead_y,fill='black',width=3,tag='lines')
            leftpos1,leftpos2,rightpos1,rightpos2=self.getHookPos((lineHead_x,lineHead_y),status='close')
            self.Board.create_line(lineHead_x,lineHead_y,leftpos1[0],leftpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(leftpos1[0],leftpos1[1],leftpos2[0],leftpos2[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(lineHead_x,lineHead_y,rightpos1[0],rightpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(rightpos1[0],rightpos1[1],rightpos2[0],rightpos2[1],fill='black',width=3,tag='Hook')
            
            _IconPos=self.getTriggerPos(15)
            catchIcon.movePos(_IconPos)
            self.ICON.moveIcon(catchIcon.name,catchIcon.posOffset(catchIcon.pos))
            
            self.root.after(20,self.HookCatch,catchIcon)
        
    def gameWin(self):
        self.Board.create_text(self.screen_width/2,self.screen_height/2,text='你获得了胜利',font=('微软雅黑',50),fill='red',tag='win')
        self.root.after(5000,self.root.destroy)
        
    def checkWin(self):
        for i in self.IconData:
            if i.TouchAble:
                return False
        return True
        
    def HookBack(self):
        if self.HookOrder:
            if self.lineChange(-1):
                self.HookOrder=False
                self.HookActive()
                return
            
            self.Board.delete('lines')
            self.Board.delete('Hook')
            lineHead_x=self.screen_width/2+self.line*math.cos(math.radians(self.angle))
            lineHead_y=self.screen_height//4+18+self.line*math.sin(math.radians(self.angle))
            self.Board.create_line(self.screen_width/2,self.screen_height//4+18,lineHead_x,lineHead_y,fill='black',width=3,tag='lines')
            leftpos1,leftpos2,rightpos1,rightpos2=self.getHookPos((lineHead_x,lineHead_y),status='close')
            self.Board.create_line(lineHead_x,lineHead_y,leftpos1[0],leftpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(leftpos1[0],leftpos1[1],leftpos2[0],leftpos2[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(lineHead_x,lineHead_y,rightpos1[0],rightpos1[1],fill='black',width=3,tag='Hook')
            self.Board.create_line(rightpos1[0],rightpos1[1],rightpos2[0],rightpos2[1],fill='black',width=3,tag='Hook')
            
            self.root.after(20,self.HookBack)
    
    def checkTrigger(self):
        if self.TriggerPos[0]<0 or self.TriggerPos[0]>self.screen_width or self.TriggerPos[1]<0 or self.TriggerPos[1]>self.screen_height:
            return -1
        else:
            _ret=self.checkInArea(self.TriggerPos)
            if _ret:
                return _ret
            else:
                return 0
        
        
    def checkInArea(self,pos):
        for _icon in self.IconData:
            if _icon.inArea(pos):
                return _icon
        return False

        
    def getHookPos(self,basepos,status):
        HookLong=20
        if status=='close':
            offsetAngle=50
        elif status=='open':
            offsetAngle=80
        left_pos_x_1=basepos[0]+HookLong*math.cos(math.radians(self.angle-offsetAngle))
        left_pos_x_2=left_pos_x_1+HookLong*math.cos(math.radians(self.angle-offsetAngle+90))
        left_pos_y_1=basepos[1]+HookLong*math.sin(math.radians(self.angle-offsetAngle))
        left_pos_y_2=left_pos_y_1+HookLong*math.sin(math.radians(self.angle-offsetAngle+90))
        right_pos_x_1=basepos[0]+HookLong*math.cos(math.radians(self.angle+offsetAngle))
        right_pos_x_2=right_pos_x_1+HookLong*math.cos(math.radians(self.angle+offsetAngle-90))
        right_pos_y_1=basepos[1]+HookLong*math.sin(math.radians(self.angle+offsetAngle))
        right_pos_y_2=right_pos_y_1+HookLong*math.sin(math.radians(self.angle+offsetAngle-90))
        return [left_pos_x_1,left_pos_y_1],[left_pos_x_2,left_pos_y_2],[right_pos_x_1,right_pos_y_1],[right_pos_x_2,right_pos_y_2]
        
    def lineChange(self,forward=0):
        if not forward:
            self.line+=self.lineOutSpeed
        else:
            if forward==1:
                self.line-=self.lineBackSpeed
            else:
                self.line-=self.lineOutSpeed
            if self.line<=self.lineMin:
                self.line=self.lineMin
                return True
    
    def angleSpeed(self):
        _speed=(1-abs(self.midAngle-self.angle)/abs(self.halfAngle))*0.8+0.2
        return round(_speed*self.speedLevel,2)
    
    def angleChange(self):
        self.angle+=self.angleForward * self.angleSpeed()
        if self.angle<=self.angleMin or self.angle>=self.angleMax:
            self.angleForward=-self.angleForward
    
    def main(self):
        self.root=Tk()
        self.screen_width=self.root.winfo_screenwidth()
        self.screen_height=self.root.winfo_screenheight()
        self.gameEnvInit()
        self.basePicData()
        self.root.geometry(f'{self.screen_width}x{self.screen_height}+0+0')
        self.root.overrideredirect(True)
        self.root.attributes("-transparentcolor", 'white')
        self.root.attributes('-topmost', True)
        self.root.bind_all('<Escape>',self.gameDestroy)
        self.root.bind_all('<Button-3>',self.gameDestroy)
        self.root.bind('<Destroy>',self.destroyTrigger)
        self.root.protocol("WM_DELETE_WINDOW", self.destroyTrigger)
        self.Board=Canvas(self.root,width=self.screen_width,height=self.screen_height,bg='#FFFFFF',relief='flat',highlightthickness=0)
        self.Board.place(x=0,y=0)
        self.Board.bind('<Button-1>',self.HookOrderTrigger)
        self.DrawBasicPlayer()
        self.root.after(20,self.HookActive)
        self.root.mainloop()

class ICONDATA():
    def __init__(self,name,id,pos_x,pos_y,areaLarge=64):
        self.name=name
        self.pos_x=pos_x
        self.pos_y=pos_y
        self.id=id
        self.pos=[pos_x,pos_y]
        self.area=[pos_x,pos_y,pos_x+areaLarge,pos_y+areaLarge]
        self.TouchAble=True
        self.areaLarge=areaLarge
    def __repr__(self):
        return f'{self.name}({self.id})'
    def movePos(self,pos):
        self.pos=pos
        self.pos_x=pos[0]
        self.pos_y=pos[1]
        self.area=[pos[0],pos[1],pos[0]+self.areaLarge,pos[1]+self.areaLarge]
    def inArea(self,pos):
        if not self.TouchAble:
            return False
        if pos[0]>=self.area[0] and pos[0]<=self.area[2] and pos[1]>=self.area[1] and pos[1]<=self.area[3]:
            return True
        else:
            return False
    def posOffset(self,pos):
        return [pos[0]-20,pos[1]-20]
    

if __name__=='__main__':
    GoldenMiner=Game()
    GoldenMiner()
