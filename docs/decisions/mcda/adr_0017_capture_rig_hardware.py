M={
"board":(["capture","power","cost","m6path","supply"],[30,20,20,15,15],
 {"A Pi5 8GB":[5,2,3,5,5],"B Pi4 4GB":[4,3,4,2,4],"C Zero2W":[2,5,5,0,3],"D Jetson Orin Nano":[4,1,1,4,3]},
 [[30,35,15,10,10],[20,20,30,15,15],[30,20,20,0,30]]),
"camera":(["px_on_hornet","motion_blur","cost","fits_head","lowlight"],[30,20,15,20,15],
 {"A CM3":[4,3,5,5,3],"B CM3 Wide":[2,3,5,5,3],"C HQ+6mm":[5,3,2,2,5],"D GS+6mm":[3,5,2,2,3]},
 [[20,35,15,15,15],[40,15,10,15,20],[30,20,15,5,30]]),
"mics":(["band_fidelity","sync_one_clock","cable_run","cost","simplicity"],[30,30,15,10,15],
 {"A 2x ICS-43434 one I2S bus":[4,5,3,5,4],"B 2x SPH0645 one I2S bus":[3,5,3,5,4],"C USB audio + 2 analog mics":[4,2,5,3,3]},
 [[30,15,30,10,15],[40,20,15,10,15]]),
"storage":(["endurance","capacity","power","cost","simplicity"],[30,25,15,15,15],
 {"A microSD HE 256GB":[2,1,5,5,5],"B USB3 SSD 1TB":[4,5,3,3,4],"C NVMe HAT 1TB":[5,5,3,3,3]},
 [[20,25,15,15,25],[40,25,15,10,10]]),
}
for k,(c,w,o,sens) in M.items():
  print("==",k,c,w)
  for n,s in o.items(): print(f"  {n}: {sum(a*b for a,b in zip(s,w))}")
  for sw in sens:
    assert sum(sw)==100
    print("  sens",sw,{n:sum(a*b for a,b in zip(s,sw)) for n,s in o.items()})
