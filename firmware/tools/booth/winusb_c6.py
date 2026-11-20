"""Serial adapter using an explicitly identified Espressif WinUSB interface.
Defaults to Jim's C6; the verified S3 native interface may be supplied explicitly.
No driver installation. Opening/reading does not change control lines.
Only esptool callers explicitly request a device reset through DTR/RTS.
Write callers must separately verify chip type and MAC before flashing.
"""
import ctypes as c,time,uuid,threading
from ctypes import wintypes as w
class GUID(c.Structure):_fields_=[('data',c.c_ubyte*16)]
class Interface(c.Structure):_fields_=[('cbSize',w.DWORD),('guid',GUID),('flags',w.DWORD),('reserved',c.c_void_p)]
class UsbInterface(c.Structure):_fields_=[('length',c.c_ubyte),('type',c.c_ubyte),('number',c.c_ubyte),('alternate',c.c_ubyte),('endpoints',c.c_ubyte),('cls',c.c_ubyte),('subclass',c.c_ubyte),('protocol',c.c_ubyte),('string',c.c_ubyte)]
class Pipe(c.Structure):_fields_=[('kind',c.c_int),('id',c.c_ubyte),('packet',c.c_ushort),('interval',c.c_ubyte)]
s=c.WinDLL('setupapi',use_last_error=True);k=c.WinDLL('kernel32',use_last_error=True);usb=c.WinDLL('winusb',use_last_error=True)
def bind(lib,name,args,result=w.BOOL):
 f=getattr(lib,name);f.argtypes=args;f.restype=result;return f
getdev=bind(s,'SetupDiGetClassDevsW',[c.POINTER(GUID),w.LPCWSTR,c.c_void_p,w.DWORD],c.c_void_p)
enum=bind(s,'SetupDiEnumDeviceInterfaces',[c.c_void_p,c.c_void_p,c.POINTER(GUID),w.DWORD,c.POINTER(Interface)])
detail=bind(s,'SetupDiGetDeviceInterfaceDetailW',[c.c_void_p,c.POINTER(Interface),c.c_void_p,w.DWORD,c.POINTER(w.DWORD),c.c_void_p])
destroy=bind(s,'SetupDiDestroyDeviceInfoList',[c.c_void_p])
create=bind(k,'CreateFileW',[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,c.c_void_p],c.c_void_p);close=bind(k,'CloseHandle',[c.c_void_p])
init=bind(usb,'WinUsb_Initialize',[c.c_void_p,c.POINTER(c.c_void_p)])
associated=bind(usb,'WinUsb_GetAssociatedInterface',[c.c_void_p,c.c_ubyte,c.POINTER(c.c_void_p)])
query=bind(usb,'WinUsb_QueryInterfaceSettings',[c.c_void_p,c.c_ubyte,c.POINTER(UsbInterface)])
querypipe=bind(usb,'WinUsb_QueryPipe',[c.c_void_p,c.c_ubyte,c.c_ubyte,c.POINTER(Pipe)])
policy=bind(usb,'WinUsb_SetPipePolicy',[c.c_void_p,c.c_ubyte,w.ULONG,w.ULONG,c.c_void_p])
writepipe=bind(usb,'WinUsb_WritePipe',[c.c_void_p,c.c_ubyte,c.c_void_p,w.ULONG,c.POINTER(w.ULONG),c.c_void_p])
readpipe=bind(usb,'WinUsb_ReadPipe',[c.c_void_p,c.c_ubyte,c.c_void_p,w.ULONG,c.POINTER(w.ULONG),c.c_void_p]);free=bind(usb,'WinUsb_Free',[c.c_void_p])
def check(ok):
 if not ok:raise c.WinError(c.get_last_error())

class SetupPacket(c.Structure):
 _pack_=1
 _fields_=[('request_type',c.c_ubyte),('request',c.c_ubyte),('value',c.c_ushort),('index',c.c_ushort),('length',c.c_ushort)]
control=bind(usb,'WinUsb_ControlTransfer',[c.c_void_p,SetupPacket,c.c_void_p,w.ULONG,c.POINTER(w.ULONG),c.c_void_p])

class Overlapped(c.Structure):
 _fields_=[('internal',c.c_size_t),('internal_high',c.c_size_t),('offset',w.DWORD),('offset_high',w.DWORD),('event',c.c_void_p)]
event_create=bind(k,'CreateEventW',[c.c_void_p,w.BOOL,w.BOOL,w.LPCWSTR],c.c_void_p)
event_reset=bind(k,'ResetEvent',[c.c_void_p])
event_wait=bind(k,'WaitForSingleObject',[c.c_void_p,w.DWORD],w.DWORD)
get_overlapped=bind(usb,'WinUsb_GetOverlappedResult',[c.c_void_p,c.POINTER(Overlapped),c.POINTER(w.ULONG),w.BOOL])
abort_pipe=bind(usb,'WinUsb_AbortPipe',[c.c_void_p,c.c_ubyte])

class WinUsbC6:
 def __init__(self,interface_match='vid_303a&pid_1001&mi_00#7&2b4e8446&2&0000'):
  self.interface_match=interface_match.lower();assert self.interface_match.startswith('vid_303a&pid_1001&mi_00#'),'Expected an explicitly identified Espressif interface'
  self.timeout=.5;self.write_timeout=5;self.baudrate=115200;self.port=self.name='winusb-c6-f0f5bd2d07ec';self.dtr=False;self.rts=False;self.is_open=False;self.buffer=bytearray();self.interfaces=[];self.condition=threading.Condition();self.stop_reader=threading.Event();self.reader_error=None;self.open()
 def open(self):
  if self.is_open:return
  g=GUID();g.data[:]=uuid.UUID('f72fe0d4-cbcb-407d-8814-9ed673d0dd6b').bytes_le
  h=getdev(c.byref(g),None,None,18);paths=[]
  try:
   for i in range(100):
    iface=Interface();iface.cbSize=c.sizeof(iface)
    if not enum(h,None,c.byref(g),i,c.byref(iface)):break
    size=w.DWORD();detail(h,c.byref(iface),None,0,c.byref(size),None);buf=c.create_string_buffer(size.value);c.cast(buf,c.POINTER(w.DWORD))[0]=8 if c.sizeof(c.c_void_p)==8 else 6
    check(detail(h,c.byref(iface),buf,size,None,None));path=c.wstring_at(c.addressof(buf)+4)
    if self.interface_match in path.lower():paths.append(path)
  finally:destroy(h)
  assert len(paths)==1,'Expected exactly the selected Espressif USB interface'
  self.handle=create(paths[0],0xc0000000,0,None,3,0x40000000,None);assert self.handle!=c.c_void_p(-1).value
  try:
   main=c.c_void_p();check(init(self.handle,c.byref(main)));self.interfaces=[main];extra=c.c_void_p()
   if associated(main,0,c.byref(extra)):self.interfaces.append(extra)
   inputs=[];outputs=[]
   for interface in self.interfaces:
    desc=UsbInterface();check(query(interface,0,c.byref(desc)))
    for index in range(desc.endpoints):
     pipe=Pipe();check(querypipe(interface,0,index,c.byref(pipe)))
     if pipe.kind==2:
      (inputs if pipe.id&128 else outputs).append((interface,pipe.id))
   assert len(inputs)==len(outputs)==1,'Expected CDC bulk input/output only';self.input=inputs[0];self.output=outputs[0];self.is_open=True;self.reader_error=None;self.stop_reader.clear();self.reader=threading.Thread(target=self._pump,daemon=True);self.reader.start()
  except BaseException:self.close();raise
 def isOpen(self):return self.is_open
 def close(self):
  self.stop_reader.set()
  if getattr(self,'is_open',False):abort_pipe(self.input[0],self.input[1])
  if getattr(self,'reader',None):self.reader.join(2)
  for interface in reversed(self.interfaces):free(interface)
  self.interfaces=[]
  if getattr(self,'handle',None):close(self.handle);self.handle=None
  self.is_open=False
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
 def _lines(self):
  transferred=w.ULONG();setup=SetupPacket(0x21,0x22,int(self.dtr)|(int(self.rts)<<1),0,0);check(control(self.interfaces[0],setup,None,0,c.byref(transferred),None))
 def setDTR(self,value):self.dtr=bool(value);self._lines()
 def setRTS(self,value):self.rts=bool(value);self._lines()
 def _pump(self):
  transfers=[]
  try:
   for _ in range(128):
    ov=Overlapped();ov.event=event_create(None,True,False,None);assert ov.event
    buf=c.create_string_buffer(64);transfers.append((ov,buf))
    ok=readpipe(self.input[0],self.input[1],buf,len(buf),None,c.byref(ov))
    if not ok and c.get_last_error()!=997:raise c.WinError(c.get_last_error())
   index=0
   while not self.stop_reader.is_set():
    ov,buf=transfers[index]
    if event_wait(ov.event,100)==258:continue
    got=w.ULONG();ok=get_overlapped(self.input[0],c.byref(ov),c.byref(got),False)
    if self.stop_reader.is_set():break
    check(ok)
    if got.value:
     with self.condition:
      self.buffer.extend(buf.raw[:got.value]);self.condition.notify_all()
    check(event_reset(ov.event));ov.internal=ov.internal_high=0
    ok=readpipe(self.input[0],self.input[1],buf,len(buf),None,c.byref(ov))
    if not ok and c.get_last_error()!=997:raise c.WinError(c.get_last_error())
    index=(index+1)%len(transfers)
  except BaseException as error:
   with self.condition:self.reader_error=error;self.condition.notify_all()
  finally:
   abort_pipe(self.input[0],self.input[1])
   for ov,buf in transfers:
    got=w.ULONG();get_overlapped(self.input[0],c.byref(ov),c.byref(got),True);close(ov.event)
 def read(self,size=1):
  if size<=0:return b''
  end=time.monotonic()+(self.timeout if self.timeout is not None else 60)
  with self.condition:
   while len(self.buffer)<size:
    if self.reader_error:raise self.reader_error
    remaining=end-time.monotonic()
    if remaining<=0:break
    self.condition.wait(remaining)
   result=bytes(self.buffer[:size]);del self.buffer[:size];return result
 def write(self,data):
  data=bytes(data);timeout=w.ULONG(max(1,int((self.write_timeout or 5)*1000)));check(policy(self.output[0],self.output[1],3,c.sizeof(timeout),c.byref(timeout)))
  offset=0
  while offset<len(data):
   chunk=data[offset:offset+64];sent=w.ULONG();check(writepipe(self.output[0],self.output[1],chunk,len(chunk),c.byref(sent),None));assert 0<sent.value<=len(chunk),'USB short write made no progress';offset+=sent.value
  return offset
 def inWaiting(self):return len(self.buffer)
 @property
 def in_waiting(self):return len(self.buffer)
 def reset_input_buffer(self):
  # Reader URBs stay queued; discard already-received bytes after a quiet moment.
  for _ in range(10):
   with self.condition:self.buffer.clear();self.condition.wait(.025);quiet=not self.buffer
   if quiet:break
  with self.condition:self.buffer.clear()
 def flushInput(self):self.reset_input_buffer()
 def flushOutput(self):pass
 def flush(self):pass
