import ctypes
import struct, commctrl, win32gui, win32con, win32api
import platform
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import pickle

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

    def updateIconsInfo(self):
        self.icons_info = self.getIconsInfo()
    
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
                win32gui.SendMessage(self.handle_desktop, commctrl.LVM_SETITEMPOSITION, self.oraginal_icons[icon_name][0], win32api.MAKELONG(pos[0],pos[1]))
                return True
            else:
                return False
        else:
            if icon_name in self.icons_info:
                win32gui.SendMessage(self.handle_desktop, commctrl.LVM_SETITEMPOSITION, self.icons_info[icon_name][0], win32api.MAKELONG(pos[0],pos[1]))
                return True
            else:
                return False
        
    def getIconPos(self,icon_name):
        # Get the icon pos
        if icon_name in self.icons_info:
            return self.icons_info[icon_name][1]
        else:
            return False
    def getIconsName(self):
        # Get the icons name
        return self.icons_info.keys()

    def recoveryIconsPos(self,oraginal=True):
        # Recovery the icons pos
        if oraginal:
            for icon in self.oraginal_icons:
                self.moveIcon(icon,self.oraginal_icons[icon][1],recovery=True)
            return True
        else:
            for icon in self.icons_info:
                self.moveIcon(icon,self.icons_info[icon][1])
            return True
        
    def recoveryIconsPosFile(self,icons):
        # Recovery the icons pos from file
        for i in range(5):
            for icon in icons:
                win32gui.SendMessage(self.handle_desktop, commctrl.LVM_SETITEMPOSITION, self.icons_info[icon][0], win32api.MAKELONG(icons[icon][1][0],icons[icon][1][1]))
            
class Tool():
    author='Aikko'
    def __init__(self):
        self.ICON=ICONCONTROL()
        
    def __call__(self):
        self.main()
    
    def saveIconFile(self):
        _tmp=self.ICON.getIconsInfo()
        try:
            with open('icon.dat','wb') as f:
                f.write(pickle.dumps(_tmp))
        except IOError:
            messagebox.showerror('Error','icon.dat save faild')
    
    def loadIconFile(self):
        try:
            with open('icon.dat','rb') as f:
                _tmp=pickle.loads(f.read())
            self.ICON.recoveryIconsPosFile(_tmp)
        except:
            messagebox.showerror('Error','No icon.dat file')
            
    
    def main(self):
        self.root=Tk()
        self.root.geometry('260x120')
        self.root.title('IconBackup')
        _Frame_icon=LabelFrame(self.root,width=250,height=110,text='Backup Icon')
        _Frame_icon.place(anchor=CENTER,relx=0.5,rely=0.5,y=-5)
        _Button_saveicon_file=Button(_Frame_icon,text='save to file',command=self.saveIconFile)
        _Button_saveicon_file.place(anchor=CENTER,relx=0.5,rely=0.33)
        _Button_loadicon_file=Button(_Frame_icon,text='load from file',command=self.loadIconFile)
        _Button_loadicon_file.place(anchor=CENTER,relx=0.5,rely=0.66)
        self.root.mainloop()
        

if __name__=='__main__':
    IconTool=Tool()
    IconTool()
